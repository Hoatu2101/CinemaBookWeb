import hashlib
import hmac
import os
import urllib.parse
from datetime import datetime, timedelta, timezone

class VNPayService:
    def __init__(self, tmn_code=None, hash_secret=None, vnp_url=None, return_url=None):
        self.tmn_code = tmn_code or getattr(settings, 'VNPAY_TMN_CODE', None) or os.getenv('VNPAY_TMN_CODE', 'QMOGOGN5')
        self.hash_secret = hash_secret or getattr(settings, 'VNPAY_HASH_SECRET', None) or os.getenv('VNPAY_HASH_SECRET', 'ARCUJSULBPRSKHSERCHGUKLCDNGXVWXC')
        self.vnp_url = vnp_url or getattr(settings, 'VNPAY_URL', None) or os.getenv('VNPAY_URL', 'https://sandbox.vnpayment.vn/paymentv2/vpcpay.html')
        self.return_url = return_url or getattr(settings, 'VNPAY_RETURN_URL', None) or os.getenv('VNPAY_RETURN_URL', 'http://localhost:8000/api/payments/vnpay-return/')

    def get_payment_url(self, order_id, amount, order_info="Thanh toan ve xem phim CineBook", ip_addr="127.0.0.1", return_url=None):
        if not return_url:
            return_url = self.return_url

        if not ip_addr or ip_addr == '::1' or ':' in ip_addr:
            ip_addr = '127.0.0.1'

        # VNPAY bắt buộc thời gian theo múi giờ Việt Nam (GMT+7)
        tz_vn = timezone(timedelta(hours=7))
        now = datetime.now(tz_vn)
        vnp_create_date = now.strftime("%Y%m%d%H%M%S")
        vnp_expire_date = (now + timedelta(minutes=15)).strftime("%Y%m%d%H%M%S")

        
        # Tạo vnp_TxnRef duy nhất bằng cách đính kèm timestamp để tránh trùng lặp mã đơn trong VNPAY Sandbox
        vnp_txn_ref = f"{order_id}_{int(now.timestamp())}"
        vnp_amount = int(float(amount) * 100)

        params = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": self.tmn_code,
            "vnp_Amount": str(vnp_amount),
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": vnp_txn_ref,
            "vnp_OrderInfo": str(order_info),
            "vnp_OrderType": "billpayment",
            "vnp_Locale": "vn",
            "vnp_ReturnUrl": return_url,
            "vnp_IpAddr": ip_addr,
            "vnp_CreateDate": vnp_create_date,
            "vnp_ExpireDate": vnp_expire_date
        }

        # 1. Sắp xếp tham số theo alphabet
        input_data = sorted(params.items())
        
        # 2. Tạo chuỗi hash_data
        hash_data = "&".join([f"{k}={urllib.parse.quote_plus(str(v))}" for k, v in input_data])

        # 3. Mã hóa HMAC-SHA512
        hash_value = hmac.new(
            self.hash_secret.encode('utf-8'),
            hash_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        payment_url = f"{self.vnp_url}?{hash_data}&vnp_SecureHash={hash_value}"
        return payment_url

    def validate_response(self, response_params):
        vnp_secure_hash = response_params.get("vnp_SecureHash", "")
        
        params = {}
        for k, v in response_params.items():
            if k.startswith("vnp_") and k not in ["vnp_SecureHash", "vnp_SecureHashType"]:
                params[k] = v

        input_data = sorted(params.items())
        has_data = ""
        seq = 0
        for key, val in input_data:
            if seq == 0:
                has_data = has_data + key + "=" + urllib.parse.quote_plus(str(val))
            else:
                has_data = has_data + "&" + key + "=" + urllib.parse.quote_plus(str(val))
            seq += 1

        calculated_hash = hmac.new(
            self.hash_secret.encode('utf-8'),
            has_data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()

        return calculated_hash.lower() == vnp_secure_hash.lower()
