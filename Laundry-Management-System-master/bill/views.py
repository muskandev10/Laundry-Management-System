import hashlib
import base64
import json
import requests
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .models import Bill, PaymentTransaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def online_billing(request, order_id=None):
    bill = None
    show_form = True
    
    order_id = order_id or request.GET.get('order_id')
    
    if order_id:
        try:
            from laundry.models import LaundryOrder
            order = LaundryOrder.objects.get(pk=order_id)
            
            # Security Check: Only the order owner or staff can see the bill
            if order.user and order.user != request.user and not request.user.is_staff:
                messages.error(request, "You are not authorized to pay for this order.")
                return redirect('home')

            price_list = {
                'washing': 40,
                'ironing': 30,
                'dry cleaning': 80,
                'wash & iron': 60,
            }

            service_text = order.laundry_type.lower()

            if 'wash & iron' in service_text:
                key = 'wash & iron'
            elif 'dry cleaning' in service_text:
                key = 'dry cleaning'
            elif 'ironing' in service_text:
                key = 'ironing'
            elif 'washing' in service_text:
                key = 'washing'
            else:
                key = None

            quantity = float(order.weight)
            price_per_unit = price_list.get(key, 0)
            total_amount = int(price_per_unit * quantity)

            # Try to find existing bill for this order
            bill = Bill.objects.filter(order=order).first()

            if bill:
                # Update existing bill to fix wrong calculations
                bill.customer_name = order.full_name
                bill.phone = order.mobile
                bill.service = f"{order.laundry_type} - {order.cloth_type}"
                bill.quantity = quantity
                bill.price = price_per_unit
                bill.total = total_amount
                bill.save()
            else:
                # Create new bill
                bill = Bill.objects.create(
                    order=order,
                    customer_name=order.full_name,
                    phone=order.mobile,
                    service=f"{order.laundry_type} - {order.cloth_type}",
                    quantity=quantity,
                    price=price_per_unit,
                    total=total_amount
                )

            show_form = False   #  hide form

        except Exception as e:
            print(f"Error auto-generating bill: {e}")

    # Handle Manual Bill Submission
    if request.method == 'POST' and not bill:
        customer_name = request.POST.get('customer_name')
        phone = request.POST.get('phone')
        service = request.POST.get('service')
        quantity = float(request.POST.get('quantity', 0))
        price = int(request.POST.get('price', 0))
        total = int(quantity * price)

        bill = Bill.objects.create(
            customer_name=customer_name,
            phone=phone,
            service=service,
            quantity=quantity,
            price=price,
            total=total
        )
        show_form = False

    return render(request, 'online_billing.html', {
        'bill': bill,
        'show_form': show_form
    })




def generate_checksum(payload_base64, endpoint):
    string = payload_base64 + endpoint + settings.PHONEPE_SALT_KEY
    sha256 = hashlib.sha256(string.encode('utf-8')).hexdigest()
    return f"{sha256}###{settings.PHONEPE_SALT_INDEX}"

def initiate_payment(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    
    # Merchant transaction ID should be unique
    merchant_transaction_id = f"MT{uuid.uuid4().hex[:10].upper()}"
    
    # Amount in paise (1 INR = 100 paise)
    amount_in_paise = int(bill.total * 100)
    
    # Create PaymentTransaction record
    transaction = PaymentTransaction.objects.create(
        bill=bill,
        merchant_transaction_id=merchant_transaction_id,
        amount=amount_in_paise,
        status='PENDING'
    )
    
    # Get the base URL dynamically from the current request
    base_url = request.build_absolute_uri('/')[:-1]
    
    # Construct Payload
    payload = {
        "merchantId": settings.PHONEPE_MERCHANT_ID,
        "merchantTransactionId": merchant_transaction_id,
        "merchantUserId": f"USER{bill.phone}",
        "amount": amount_in_paise,
        "redirectUrl": f"{base_url}/bill/payment-callback/?transactionId={merchant_transaction_id}",
        "redirectMode": "POST",
        "callbackUrl": f"{base_url}/bill/payment-callback/",
        "mobileNumber": bill.phone,
        "paymentInstrument": {
            "type": "PAY_PAGE"
        }
    }
    
    # Encode payload
    payload_json = json.dumps(payload)
    payload_base64 = base64.b64encode(payload_json.encode('utf-8')).decode('utf-8')
    
    # Generate Checksum
    checksum = generate_checksum(payload_base64, "/pg/v1/pay")
    
    # Call PhonePe API
    headers = {
        "Content-Type": "application/json",
        "X-VERIFY": checksum,
        "accept": "application/json"
    }
    
    api_payload = {
        "request": payload_base64
    }
    
    try:
        response = requests.post(settings.PHONEPE_API_ENDPOINT, json=api_payload, headers=headers)
        res_data = response.json()
        
        if res_data.get('success'):
            redirect_url = res_data['data']['instrumentResponse']['redirectInfo']['url']
            return redirect(redirect_url)
        else:
            return HttpResponse(f"Payment initiation failed: {res_data.get('message')}")
            
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}")

def check_payment_status_api(merchant_transaction_id):
    endpoint = f"/pg/v1/status/{settings.PHONEPE_MERCHANT_ID}/{merchant_transaction_id}"
    string = endpoint + settings.PHONEPE_SALT_KEY
    sha256 = hashlib.sha256(string.encode('utf-8')).hexdigest()
    checksum = f"{sha256}###{settings.PHONEPE_SALT_INDEX}"
    
    headers = {
        "Content-Type": "application/json",
        "X-VERIFY": checksum,
        "X-MERCHANT-ID": settings.PHONEPE_MERCHANT_ID,
        "accept": "application/json"
    }
    
    url = f"{settings.PHONEPE_STATUS_ENDPOINT}/{settings.PHONEPE_MERCHANT_ID}/{merchant_transaction_id}"
    
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except:
        return None

@csrf_exempt
def payment_callback(request):
    merchant_transaction_id = None
    
    if request.method == "POST":
        response_base64 = request.POST.get('response')
        if response_base64:
            response_json = base64.b64decode(response_base64).decode('utf-8')
            response_data = json.loads(response_json)
            merchant_transaction_id = response_data.get('data', {}).get('merchantTransactionId')
    
    # If not in POST, check query params or alternative POST fields
    if not merchant_transaction_id:
        merchant_transaction_id = request.GET.get('transactionId') or \
                                 request.GET.get('merchantTransactionId') or \
                                 request.POST.get('merchantTransactionId')

    # Debug logging for console
    print(f"--- Payment Callback Received ---")
    print(f"Method: {request.method}")
    print(f"Merchant Transaction ID: {merchant_transaction_id}")

    error_message = None
    if merchant_transaction_id:
        # For security, always double check status with API
        status_res = check_payment_status_api(merchant_transaction_id)
        
        if status_res:
            status_code = status_res.get('code')
            status_success = status_res.get('success')
            message = status_res.get('message', 'No message from provider')
            
            transaction = PaymentTransaction.objects.filter(merchant_transaction_id=merchant_transaction_id).first()
            
            if transaction:
                # If PhonePe says success OR the code matches success
                if status_success and status_code == 'PAYMENT_SUCCESS':
                    transaction.status = 'SUCCESS'
                    transaction.bill.payment_status = 'Paid'
                    transaction.bill.save()
                    transaction.save()
                    return render(request, 'payment_callback.html', {
                        'status': 'SUCCESS', 
                        'bill': transaction.bill,
                        'transaction_id': merchant_transaction_id
                    })
                else:
                    transaction.status = 'FAILED'
                    transaction.save()
                    error_message = f"PhonePe Code: {status_code} - {message}"
                    return render(request, 'payment_callback.html', {
                        'status': 'FAILED', 
                        'bill': transaction.bill,
                        'transaction_id': merchant_transaction_id,
                        'error_message': error_message
                    })
            else:
                error_message = f"Transaction record not found in database for ID: {merchant_transaction_id}"
        else:
            error_message = "Unable to verify payment status with PhonePe API (Status API failed)"
    else:
        error_message = "No Transaction ID received from payment gateway"
        
    return render(request, 'payment_callback.html', {
        'status': 'FAILED',
        'error_message': error_message
    })
def payment_status(request):
    bill_id = request.GET.get('bill_id')
    bill = None

    if bill_id:
        bill = Bill.objects.filter(id=bill_id).first()

    return render(request, 'payment_status.html', {
        'bill': bill
    })
