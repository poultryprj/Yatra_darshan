
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
import requests
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa
from PIL import Image  
import os, uuid, json
from django.conf import settings
from django.http import JsonResponse
from django.db import transaction

headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://www.gyaagl.app",
    "Referer": "https://www.gyaagl.app/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

API_BASE_URL = "http://127.0.0.1:8000/LakshyaPratishthan/api/"

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')    
    
    if request.method == 'POST':
        print("24")
        mobile = request.POST.get('mobile')
        pin = request.POST.get('pin_number')
        # api_url = 'https://www.lakshyapratishthan.com/apis/agentlogin'
        api_url = f"{API_BASE_URL}agentlogin/"
        payload = {
            "userMobileNo": mobile,
            "userPassword": pin,
        }
        print(payload,"197")
        
        try:
            response = requests.post(api_url, json=payload, headers=headers, verify= False, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(data)

                if data.get("message_code") == 1000:
                    user_info = data["message_data"][0]
                    request.session["user_id"] = user_info["UserId"]
                    request.session["first_name"] = user_info["UserFirstname"]
                    request.session["last_name"] = user_info["UserLastname"]
                    request.session["user_role"] = user_info["UserRole"]
                    return redirect('Registrationpage1')
                    # messages.success(request, data.get("message_text", "Login successful."))
                else:
                    messages.error(request, data.get("message_text", "Invalid mobile number or PIN."))
            else:
                messages.error(request, f"HTTP Error {response.status_code}")

        except Exception as e:
            print("Login Exception:", e)
            messages.error(request, "Unable to login. Please try again later.")

        return redirect('login')
    
def Registrationpage(request):
    """
    Render Registration page after login with user details.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user_details = {
        "first_name": request.session.get("first_name", ""),
        "last_name": request.session.get("last_name", ""),
        "mobile_no": request.session.get("mobile_no", ""),
        "aadhar_no": request.session.get("aadhar_no", ""),
        "user_role": request.session.get("user_role", ""),
    }

    route_yatras_data = []
    api_url = "https://www.lakshyapratishthan.com/apis/routeyatradates"

    try:
        response = requests.get(api_url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("Route Yatra API Response:", data)

            if str(data.get("message_code")) == "1000":
                route_yatras_data = data.get("message_data", [])
            else:
                messages.error(request, data.get("message_text", "Unable to fetch route yatra dates."))
        else:
            messages.error(request, f"HTTP Error {response.status_code}")
    except Exception as e:
        print("Route Yatra API Exception:", e)
        messages.error(request, "Unable to fetch route yatra dates. Please try again later.")

    return render(request, "registration.html", {
        "user": user_details,
        "route_yatras": route_yatras_data
    })

@csrf_exempt
def registration_api(request):
    """
    Unified API proxy for Registration page.
    Handles search, list_area, list_gender, list_bloodgroup.
    """
    if request.method == "POST":
        action = request.POST.get("action")

        action = request.POST.get("action")
        try:
            if action == "search":
                mobile = request.POST.get("search")
                api_url = "https://www.lakshyapratishthan.com/apis/searchregistrations"
                payload = {"mobile_no": mobile}
                response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    msg_code = str(data.get("message_code"))

                    if msg_code == "1000":
                        records = data.get("message_data", [])
                        if records and isinstance(records, list):
                            latest = records[0]  # take first record
                            result = {
                                "RegistrationId": latest.get("RegistrationId", ""),
                                "Firstname": latest.get("Firstname", ""),
                                "Lastname": latest.get("Lastname", ""),
                                "Middlename": latest.get("Middlename", ""),
                                "MobileNo": latest.get("MobileNo", ""),
                                "AlternateMobileNo": latest.get("AlternateMobileNo", ""),
                                "AadharNumber": latest.get("AadharNumber", ""),
                                "DateOfBirth": latest.get("DateOfBirth", ""),
                                "Gender": latest.get("Gender", ""),
                                "BloodGroup": latest.get("BloodGroup", ""),
                                "AreaId": latest.get("AreaId", "") or latest.get("AreaName", ""),
                                "Address": latest.get("Address", ""),
                            }
                            return JsonResponse({
                                "message_code": 1000,
                                "message_text": "Registration details fetched successfully.",
                                "message_data": result
                            })

                    # API returned 999 or empty data → clear fields
                    return JsonResponse({
                        "message_code": 999,
                        "message_text": "User not registered."
                    })

            elif action == "list_area":
                api_url = "https://www.lakshyapratishthan.com/apis/listarea"
                response = requests.get(api_url, headers=headers, verify=False, timeout=10)

            elif action == "list_gender":
                api_url = "https://www.lakshyapratishthan.com/apis/listgender"
                response = requests.get(api_url, headers=headers, verify=False, timeout=10)

            elif action == "list_bloodgroup":
                api_url = "https://www.lakshyapratishthan.com/apis/listbloodgroup"
                response = requests.get(api_url, headers=headers, verify=False, timeout=10)

            elif action == "submit":
                api_url = "https://www.lakshyapratishthan.com/apis/pilgrimregistration"

                dob_str = request.POST.get("DateOfBirth", "")
                dob_final = ""
                if dob_str:
                    try:
                        from datetime import datetime
                        dob_final = datetime.strptime(dob_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                    except Exception:
                        dob_final = dob_str
                 # ✅ Handle file uploads
                aadhar_file = request.FILES.get("AadharUpload")
                profile_file = request.FILES.get("ProfilePicUpload")
                voterId_File = request.FILES.get("VoterIdUpload")

                aadhar_url, profile_url = None, None

                # --- Save Aadhar ---
                if aadhar_file:
                    file_name = f"{uuid.uuid4().hex}.png"  # always PNG
                    img_directory = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "adhar")
                    os.makedirs(img_directory, exist_ok=True)
                    save_path = os.path.join(img_directory, file_name)

                    # Convert to PNG and save
                    image = Image.open(aadhar_file)
                    image = image.convert("RGB")  # ensure compatibility
                    image.save(save_path, "PNG")

                    aadhar_url = f"https://www.lakshyapratishthan.com/Yatra_darshan/static/assets/adhar/{file_name}"
                    print("Aadhar saved at:", save_path)
                    print("Aadhar URL:", aadhar_url)

                # --- Save Profile Pic ---
                if profile_file:
                    file_name = f"{uuid.uuid4().hex}.png"  # always PNG
                    img_directory = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "profile")
                    os.makedirs(img_directory, exist_ok=True)
                    save_path = os.path.join(img_directory, file_name)

                    # Convert to PNG and save
                    image = Image.open(profile_file)
                    image = image.convert("RGB")  # ensure compatibility
                    image.save(save_path, "PNG")

                    profile_url = f"https://www.lakshyapratishthan.com/Yatra_darshan/static/assets/profile/{file_name}"
                    print("Profile saved at:", save_path)
                    print("Profile URL:", profile_url)
                    
                    
                # --- Save VoterID Pic ---
                if voterId_File:
                    file_name = f"{uuid.uuid4().hex}.png"  # always PNG
                    img_directory = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "voterId")
                    os.makedirs(img_directory, exist_ok=True)
                    save_path = os.path.join(img_directory, file_name)

                    # Convert to PNG and save
                    image = Image.open(voterId_File)
                    image = image.convert("RGB")  # ensure proper format
                    image.save(save_path, "PNG")

                    voterId_url = f"https://www.lakshyapratishthan.com/Yatra_darshan/static/assets/voterId/{file_name}"
                    print("VoterId saved at:", save_path)
                    print("VoterId URL:", voterId_url)

                payload = {
                    "RegistrationId": request.POST.get("RegistrationId", 0),
                    "userMobileNo": request.POST.get("userMobileNo"),   # ✅ keep exact key
                    "userFirstname": request.POST.get("userFirstname"),
                    "userMiddlename": request.POST.get("userMiddlename", ""),
                    "userLastname": request.POST.get("userLastname"),
                    "AreaId": request.POST.get("AreaId", 1),
                    "Gender": request.POST.get("Gender", 1),
                    "Address": request.POST.get("Address", ""),
                    "userAlternateMobileNo": request.POST.get("userAlternateMobileNo", ""),
                    "BloodGroup": request.POST.get("BloodGroup", "Select"),  # ✅ text like "O+"
                    "DateOfBirth": dob_final,
                    "Photo": request.POST.get("Photo", ""),
                    "PhotoId": request.POST.get("PhotoId", ""),
                    "UserId": request.session.get("user_id", 0),
                    # "ZonePreference": request.POST.get("ZonePreference", 0),
                    "VoterId":voterId_url,
                    
                }

                print("➡️ Calling:", api_url)
                print("➡️ Payload:", payload)

                response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

            elif action == "book_ticket":
                api_url = "https://www.lakshyapratishthan.com/apis/inserttickets"

                # Collect multiple YatraIds and join into comma-separated string
                yatra_ids = request.POST.getlist("YatraIds[]", [])
                yatra_ids_str = ",".join(yatra_ids)

                payload = {
                    "RegistrationId": request.POST.get("RegistrationId", ""),
                    "UserId": str(request.session.get("user_id", "")),
                    "YatraIds": yatra_ids_str,   # ✅ Comma-separated string
                    "AmountPaid": request.POST.get("AmountPaid", "0"),
                    "Discount": request.POST.get("Discount", "0"),
                    "DiscountReason": request.POST.get("DiscountReason", ""),
                    "PaymentId": request.POST.get("PaymentId", ""),
                }

                print("➡️ Ticket Booking Payload (final):", payload)

                response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)    
            else:
                return JsonResponse({"message_code": 999, "message_text": "Invalid action"})

            if response.status_code == 200:
                return JsonResponse(response.json(), safe=False)
            else:
                return JsonResponse({"message_code": 999, "message_text": f"HTTP Error {response.status_code}"})

        except Exception as e:
            return JsonResponse({"message_code": 999, "message_text": f"Exception: {str(e)}"})

    return JsonResponse({"message_code": 999, "message_text": "Invalid request method"})


def Registrationpage1(request):
    """
    Render Registration page after login with user details.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user_details = {
        "first_name": request.session.get("first_name", ""),
        "last_name": request.session.get("last_name", ""),
        "mobile_no": request.session.get("mobile_no", ""),
        "aadhar_no": request.session.get("aadhar_no", ""),
        "user_role": request.session.get("user_role", ""),
    }

    # If you still need route_yatras later for booking, keep this block
    route_yatras_data = []
    # api_url = "https://www.lakshyapratishthan.com/apis/routeyatradates"
    api_url = f"{API_BASE_URL}routeyatradates/"
    try:
        # resp = requests.get(api_url, headers=headers, verify=False, timeout=10)
        resp = requests.get(api_url,verify=False)
        if resp.status_code == 200:
            data = resp.json()
            if str(data.get("message_code")) == "1000":
                route_yatras_data = data.get("message_data", [])
            else:
                messages.error(request, data.get("message_text", "Unable to fetch route yatra dates."))
        else:
            messages.error(request, f"HTTP Error {resp.status_code}")
    except Exception as e:
        messages.error(request, "Unable to fetch route yatra dates. Please try again later.")

    return render(request, "Registration1.html", {
        "user": user_details,
        "route_yatras": route_yatras_data
    })

@csrf_exempt
def registration_api1(request):
    """
    Unified API proxy for Registration page.
    Added:
      - action=search_list -> returns FULL list of registrations for a mobile
      - action=submit      -> insert/update pilgrim (keys aligned to external API)
      - list_area / list_gender / list_bloodgroup passthrough
    """
    if request.method != "POST":
        return JsonResponse({"message_code": 999, "message_text": "Invalid request method"})

    action = request.POST.get("action")
    try:
        if action == "search_list":
            mobile = request.POST.get("search")
            # api_url = "https://www.lakshyapratishthan.com/apis/searchregistrations"
            api_url = f"{API_BASE_URL}searchregistrations/"
            payload = {"search": mobile}
            # response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
            response = requests.post(api_url, json=payload,verify=False)

            if response.status_code != 200:
                return JsonResponse({"message_code": 999, "message_text": f"HTTP Error {response.status_code}"})
            
            data = response.json()
            if str(data.get("message_code")) == "1000":
                from datetime import datetime
                # 🔥 FETCH AREA LOOKUP TABLE
                area_lookup = {}
                try:
                    # area_api_url = "https://www.lakshyapratishthan.com/apis/listarea"
                    area_api_url = f"{API_BASE_URL}listarea/"
                    # area_resp = requests.get(area_api_url, headers=headers, verify=False, timeout=10)
                    area_resp = requests.get(area_api_url,verify=False)
                    if area_resp.status_code == 200:
                        area_data = area_resp.json()
                        if str(area_data.get("message_code")) == "1000":
                            for area in area_data.get("message_data", []):
                                area_lookup[area.get("AreaName", "")] = area.get("AreaId", "1")
                except Exception as e:
                    print(f"Failed to fetch area lookup: {e}")

                rows = []
                for r in data.get("message_data", []):
                    dob_raw = r.get("DateOfBirth")
                    dob_fmt = ""
                    try:
                        if dob_raw and dob_raw.isdigit():
                            dob_fmt = datetime.fromtimestamp(int(dob_raw)).strftime("%d-%m-%Y")
                        else:
                            dob_fmt = dob_raw or ""
                    except Exception:
                        dob_fmt = dob_raw or ""

                    # 🔥 FIX: Map Gender value to proper IDs
                    gender_raw = r.get("Gender", "0")
                    gender_id = "1"  # Default to "Select"
                    gender_name = "Select"
                    
                    if str(gender_raw) == "2":
                        gender_id = "2"
                        gender_name = "Male"
                    elif str(gender_raw) == "3":
                        gender_id = "3" 
                        gender_name = "Female"
                    elif str(gender_raw) == "4":
                        gender_id = "4"
                        gender_name = "Custom"

                    # 🔥 FIX: Handle BloodGroup properly
                    # blood_group_name = r.get("BloodGroup", "").strip()
                    blood_group_name = (r.get("BloodGroup") or "").strip()
                    blood_group_id = "1"  # Default to "Select"
                    
                    # Map blood group names to IDs
                    blood_group_mapping = {
                        "A+": "2", "A-": "3", "B+": "4", "B-": "5",
                        "O+": "6", "O-": "7", "AB+": "8", "AB-": "9"
                    }
                    if blood_group_name in blood_group_mapping:
                        blood_group_id = blood_group_mapping[blood_group_name]
                    elif not blood_group_name:
                        blood_group_name = "Select"
                        
                    # 🔥 FIX: Get AreaId from AreaName using lookup table
                    area_name = r.get("AreaName", "")
                    area_id = area_lookup.get(area_name, "1")  # Default to "1" if not found

                    rows.append({
                        "RegistrationId": r.get("RegistrationId"),
                        "Firstname": r.get("Firstname"),
                        "Middlename": r.get("Middlename"),
                        "Lastname": r.get("Lastname"),
                        "MobileNo": r.get("MobileNo"),
                        "AlternateMobileNo": r.get("AlternateMobileNo"),
                        "AadharNumber": r.get("AadharNumber"),
                        "DateOfBirth": dob_fmt,
                        "Gender": gender_raw,
                        "GenderId": gender_id,  # 🔥 Added missing GenderId
                        "GenderName": gender_name,  # 🔥 Added missing GenderName
                        "BloodGroup": blood_group_name,
                        "BloodGroupId": blood_group_id,  # 🔥 Added missing BloodGroupId
                        "AreaId": area_id,  # 🔥 Make sure AreaId is included
                        "AreaName": area_name,
                        "Address": r.get("Address"),
                        "PhotoFileName": r.get("PhotoFileName"),
                        "IdProofFileName": r.get("IdProofFileName"),
                        "VoterIdProof": r.get("VoterIdProof"),
                    })
                        
                return JsonResponse({"message_code": 1000, "message_text": "OK", "message_data": rows})

            return JsonResponse({"message_code": 999, "message_text": data.get("message_text", "No data")})

        elif action == "list_area":
            # api_url = "https://www.lakshyapratishthan.com/apis/listarea"
            api_url = f"{API_BASE_URL}listarea/"
            # resp = requests.get(api_url, headers=headers, verify=False, timeout=10)
            resp = requests.get(api_url, verify=False)
            return JsonResponse(resp.json(), safe=False, status=200 if resp.status_code == 200 else 500)

        elif action == "list_gender":
            # api_url = "https://www.lakshyapratishthan.com/apis/listgender"
            api_url = f"{API_BASE_URL}listgender/"
            # resp = requests.get(api_url, headers=headers, verify=False, timeout=10)
            resp = requests.get(api_url,verify=False)
            return JsonResponse(resp.json(), safe=False, status=200 if resp.status_code == 200 else 500)
        
        elif action == "book_ticket":
            try:
                user_id = request.POST.get("UserId")
                amount_paid = request.POST.get("AmountPaid")
                discount = request.POST.get("Discount", 0)
                discount_reason = request.POST.get("DiscountReason", "")
                payment_id = request.POST.get("PaymentId")

                # 🔹 Normalize Payment Mode
                payment_mode_raw = request.POST.get("PaymentMode", "").lower()
                if payment_mode_raw == "cash":
                    payment_mode = 1
                elif payment_mode_raw == "upi":
                    payment_mode = 2
                else:
                    payment_mode = 1  # fallback

                transaction_id = request.POST.get("TransactionId", "")
                bookings_json = request.POST.get("Bookings", "[]")
                bookings = json.loads(bookings_json)
                
                # 🔹 Counts
                GroupCount = request.POST.get("Count1", "0")
                CurrentTicket = request.POST.get("Count2", "0")
                BalanceTicket = request.POST.get("Count3", "0")

                print("GroupCount:", GroupCount)
                print("CurrentTicket:", CurrentTicket)
                print("BalanceTicket:", BalanceTicket)

                # ✅ Handle UPI Screenshot upload
                upi_file = request.FILES.get("UPIScreenshot")
                trasection_url = None
                if upi_file:
                    ext = os.path.splitext(upi_file.name)[1].lower()  # original extension
                    file_name = f"{uuid.uuid4().hex}"  # unique name without extension

                    img_directory = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "trasection")
                    os.makedirs(img_directory, exist_ok=True)

                    if ext == ".pdf":
                        # Save as PDF directly
                        save_path = os.path.join(img_directory, f"{file_name}.pdf")
                        with open(save_path, "wb+") as dest:
                            for chunk in upi_file.chunks():
                                dest.write(chunk)
                        trasection_url = f"https://www.lakshyapratishthan.com/Yatra_darshan/static/assets/trasection/{file_name}.pdf"

                    else:
                        # Convert and save as PNG
                        save_path = os.path.join(img_directory, f"{file_name}.png")
                        image = Image.open(upi_file)
                        image.save(save_path, "PNG")
                        trasection_url = f"https://www.lakshyapratishthan.com/Yatra_darshan/static/assets/trasection/{file_name}.png"

                    print("UPI Screenshot saved at:", save_path)
                    print("UPI Screenshot URL:", trasection_url)
                    
                # ✅ Call external API
                # api_url = "https://www.lakshyapratishthan.com/apis/inserttickets"
                api_url = f"{API_BASE_URL}inserttickets/"

                with transaction.atomic():
                    api_responses = []
                    for b in bookings:
                        yatra_ids = b["YatraIds"]
                        if isinstance(yatra_ids, list):
                            yatra_ids = ",".join(str(y) for y in yatra_ids)

                        payload = {
                            "RegistrationId": str(b["RegistrationId"]),
                            "UserId": str(user_id),
                            "YatraIds": yatra_ids,
                            "AmountPaid": str(amount_paid),
                            "Discount": str(discount),
                            "DiscountReason": str(discount_reason),
                            "PaymentId": str(payment_id or ""),
                            "PaymentMode": payment_mode,  # ✅ 1 for cash, 2 for UPI
                            "TransactionId": str(transaction_id or ""),
                            "BalanceTicket": BalanceTicket,
                            "CurrentTicket": CurrentTicket,
                            "GroupCount": GroupCount
                        }
                        print("547",payload)
                        # r = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
                        r = requests.post(api_url, json=payload,verify=False)
                        api_response = r.json()
                        print("API Response:", api_response)

                        if api_response.get("message_code") != 1000:
                            raise Exception(api_response.get("message_text", "Booking failed"))

                        api_responses.append(api_response)

                    # ✅ Return message_data from last API response
                    last_message_data = api_responses[-1].get("message_data") if api_responses else {}

                    return JsonResponse({
                        "message_code": 1000,
                        "message_text": "Tickets booked successfully",
                        "message_data": last_message_data
                    })

            except Exception as e:
                return JsonResponse({
                    "message_code": 999,
                    "message_text": f"Error: {str(e)}"
                })

        elif action == "list_bloodgroup":
            # api_url = "https://www.lakshyapratishthan.com/apis/listbloodgroup"
            api_url = f"{API_BASE_URL}listbloodgroup/"
            # resp = requests.get(api_url, headers=headers, verify=False, timeout=10)
            resp = requests.get(api_url,verify=False)
            return JsonResponse(resp.json(), safe=False, status=200 if resp.status_code == 200 else 500)

        elif action == "submit":
            try:
                api_url = f"{API_BASE_URL}pilgrimregistration/"

                # --- File upload logic remains the same ---
                aadhar_file = request.FILES.get("AadharUpload")
                profile_file = request.FILES.get("ProfilePicUpload")
                voterId_File = request.FILES.get("VoterIdUpload")

                aadhar_url, profile_url, voterId_url = None, None, None

                # (Keep all your file saving code here, it is correct)
                # --- Save Aadhar ---
                if aadhar_file:
                    ext = os.path.splitext(aadhar_file.name)[1].lower()
                    file_name = f"{uuid.uuid4().hex}"
                    img_directory = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "adhar")
                    os.makedirs(img_directory, exist_ok=True)
                    if ext == ".pdf":
                        save_path = os.path.join(img_directory, f"{file_name}.pdf")
                        with open(save_path, "wb+") as dest:
                            for chunk in aadhar_file.chunks():
                                dest.write(chunk)
                        aadhar_url = f"https://www.lakshyapratishthan.com/Yatra_darshan/static/assets/adhar/{file_name}.pdf"
                    else:
                        save_path = os.path.join(img_directory, f"{file_name}.png")
                        image = Image.open(aadhar_file)
                        image = image.convert("RGB")
                        image.save(save_path, "PNG")
                        aadhar_url = f"https://www.lakshyapratishthan.com/Yatra_darshan/static/assets/adhar/{file_name}.png"

                # --- Save Profile Pic ---
                if profile_file:
                    ext = os.path.splitext(profile_file.name)[1].lower()
                    file_name = f"{uuid.uuid4().hex}"
                    img_directory = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "profile")
                    os.makedirs(img_directory, exist_ok=True)
                    if ext == ".pdf":
                        save_path = os.path.join(img_directory, f"{file_name}.pdf")
                        with open(save_path, "wb+") as dest:
                            for chunk in profile_file.chunks():
                                dest.write(chunk)
                        profile_url = f"https://www.lakshyapratishthan.com/Yatra_darshan/static/assets/profile/{file_name}.pdf"
                    else:
                        save_path = os.path.join(img_directory, f"{file_name}.png")
                        image = Image.open(profile_file)
                        image = image.convert("RGB")
                        image.save(save_path, "PNG")
                        profile_url = f"https://www.lakshyapratishthan.com/Yatra_darshan/static/assets/profile/{file_name}.png"

                # --- Save VoterID Pic ---
                if voterId_File:
                    ext = os.path.splitext(voterId_File.name)[1].lower()
                    file_name = f"{uuid.uuid4().hex}"
                    img_directory = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "voterId")
                    os.makedirs(img_directory, exist_ok=True)
                    if ext == ".pdf":
                        save_path = os.path.join(img_directory, f"{file_name}.pdf")
                        with open(save_path, "wb+") as dest:
                            for chunk in voterId_File.chunks():
                                dest.write(chunk)
                        voterId_url = f"https://www.lakshyapratishthan.com/Yatra_darshan/static/assets/voterId/{file_name}.pdf"
                    else:
                        save_path = os.path.join(img_directory, f"{file_name}.png")
                        image = Image.open(voterId_File)
                        image = image.convert("RGB")
                        image.save(save_path, "PNG")
                        voterId_url = f"https://www.lakshyapratishthan.com/Yatra_darshan/static/assets/voterId/{file_name}.png"
                
                # --- Intelligent Payload Preparation ---
                dob_in = request.POST.get("DateOfBirth", "")
                dob_final = dob_in
                if dob_in and "-" in dob_in and "/" not in dob_in:
                    try:
                        from datetime import datetime
                        dob_final = datetime.strptime(dob_in, "%Y-%m-%d").strftime("%d/%m/%Y")
                    except Exception:
                        pass

                payload = {
                    "userMobileNo": request.POST.get("userMobileNo"),
                    "userFirstname": request.POST.get("userFirstname"),
                    "userMiddlename": request.POST.get("userMiddlename", ""),
                    "userLastname": request.POST.get("userLastname"),
                    "AreaId": request.POST.get("AreaId", "1"),
                    "Gender": request.POST.get("Gender", "1"),
                    "Address": request.POST.get("Address", ""),
                    "userAlternateMobileNo": request.POST.get("userAlternateMobileNo", ""),
                    "BloodGroup": request.POST.get("BloodGroup", "Select"),
                    "DateOfBirth": dob_final,
                    "UserId": str(request.session.get("user_id", "0")),
                    "Photo": profile_url or request.POST.get("PhotoFileName", ""),
                    "PhotoId": aadhar_url or request.POST.get("IdProofFileName", ""),
                    "VoterId": voterId_url or request.POST.get("VoterId", ""),
                }
                
                payload["PhotoFileName"] = payload["Photo"]
                payload["IdProofFileName"] = payload["PhotoId"]

                registration_id = request.POST.get("RegistrationId", "0")

                # ✅ THE CRUCIAL FIX:
                # If the registration_id is NOT '0', it's an update.
                # Only then do we add the 'RegistrationId' key to the payload.
                # If it IS '0', the key is omitted, signaling a NEW registration.
                if registration_id != "0":
                    payload["RegistrationId"] = registration_id

                print("✅ Final Payload being sent to External API:", payload) 

                resp = requests.post(api_url, json=payload, verify=False)
                
                if resp.status_code not in [200, 201]:
                    return JsonResponse({"message_code": 999, "message_text": f"API HTTP Error {resp.status_code}"})
                
                response_data = resp.json()
                print("✅ Response Received from External API:", response_data)
                return JsonResponse(response_data, safe=False)

            except Exception as e:
                print(f"❌ Exception in submit action: {str(e)}")
                return JsonResponse({"message_code": 999, "message_text": f"Exception: {str(e)}"})

        else:
            return JsonResponse({"message_code": 999, "message_text": "Invalid action"})

    except Exception as e:
        return JsonResponse({"message_code": 999, "message_text": f"Exception: {str(e)}"})


def route_master(request):
    """
    Displays the list of all Yatra routes.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')
    
    api_url = "https://www.lakshyapratishthan.com/apis/listrouteall"
    
    try:
        response = requests.get(api_url, headers=headers, verify=False, timeout=10)
        data = response.json() if response.status_code == 200 else {}
    except Exception as e:
        print(f"Error fetching route list: {e}")
        data = {"message_code": 999, "message_text": str(e), "message_data": []}
        messages.error(request, f"Could not fetch routes: {e}")

    routes = data.get("message_data", [])
    routes = [route for route in routes if route.get("YatraRouteId") != "0"]
    return render(request, "route_master.html", {"routes": routes})


@csrf_exempt
def route_master_api(request):
    """
    API to handle adding a new route and updating route information.
    """
    if 'user_id' not in request.session:
        return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        try:
            if action == 'add_route':
                api_url = "https://www.lakshyapratishthan.com/apis/insertroute"
                payload = {
                    "YatraRouteName": request.POST.get('routeName'),
                    "YatraRouteDetails": request.POST.get('routeDetails'),
                    "YatraRouteStatus": int(request.POST.get('status')) 
                }
                response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

            elif action == 'update_route':
                route_id = request.POST.get('routeId')
                if not route_id:
                    return JsonResponse({
                        "message_code": 999,
                        "message_text": "Error: Route ID was not provided for the update."
                    })

                api_url = "https://www.lakshyapratishthan.com/apis/modifyroute"
                payload = {
                    "YatraRouteId": int(route_id),
                    "YatraRouteName": request.POST.get('routeName'),
                    "YatraRouteDetails": request.POST.get('routeDetails'),
                    "YatraRouteStatus": int(request.POST.get('status'))
                }
                response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
            
            else:
                return JsonResponse({"status": "error", "message": "Invalid action."})

            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                error_detail = response.text
                return JsonResponse({
                    "status": "error", 
                    "message": f"API Error: {response.status_code}",
                    "detail": error_detail
                }, status=response.status_code)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An exception occurred: {str(e)}"})
    return JsonResponse({"status": "error", "message": "Invalid request method."})


def area_master(request):
    """
    Displays the list of all Areas.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')
    
    api_url = "https://www.lakshyapratishthan.com/apis/listareaall"
    
    try:
        response = requests.get(api_url, headers=headers, verify=False, timeout=10)
        data = response.json() if response.status_code == 200 else {}
    except Exception as e:
        print(f"Error fetching area list: {e}")
        data = {"message_code": 999, "message_text": str(e), "message_data": []}
        messages.error(request, f"Could not fetch areas: {e}")

    areas = data.get("message_data", [])
    return render(request, "area_master.html", {"areas": areas})


@csrf_exempt
def area_master_api(request):
    """
    API to handle adding and updating areas.
    """
    if 'user_id' not in request.session:
        return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        try:
            if action == 'add_area':
                api_url = "https://www.lakshyapratishthan.com/apis/insertarea"
                payload = {
                    "AreaName": request.POST.get('areaName'),
                }
                response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

            elif action == 'update_area':
                api_url = "https://www.lakshyapratishthan.com/apis/modifyarea"
                area_id = request.POST.get('areaId')
                if not area_id:
                    return JsonResponse({"message_code": 999, "message_text": "Area ID is required for modification."})
                
                payload = {
                    "AreaId": int(area_id),
                    "AreaName": request.POST.get('areaName'),
                    "AreaStatus": request.POST.get('status') # Send as string "1" or "0"
                }
                response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
            
            else:
                return JsonResponse({"status": "error", "message": "Invalid action."})

            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({"status": "error", "message": f"API Error: {response.status_code}"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An exception occurred: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid request method."})


def yatra_master(request):
    """
    Displays the list of all Yatras and fetches routes for the dropdown.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')
    
    yatras = []
    routes = []
    try:
        yatra_api_url = "https://www.lakshyapratishthan.com/apis/listyatraall"
        response = requests.get(yatra_api_url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            yatras = response.json().get("message_data", [])
    except Exception as e:
        messages.error(request, f"Could not fetch Yatra list: {e}")
    try:
        route_api_url = "https://www.lakshyapratishthan.com/apis/listrouteall"
        response = requests.get(route_api_url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            all_routes = response.json().get("message_data", [])
            routes = [r for r in all_routes if r.get("YatraRouteId") != "0"]
    except Exception as e:
        messages.error(request, f"Could not fetch Route list: {e}")

    return render(request, "yatra_master.html", {"yatras": yatras, "routes": routes})



@csrf_exempt
def yatra_master_api(request):
    """
    API to handle adding and updating Yatras.
    """
    if 'user_id' not in request.session:
        return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        try:
            date_time = request.POST.get('dateTime')
            if action == 'add_yatra':
                api_url = "https://www.lakshyapratishthan.com/apis/insertyatra"
                payload = {
                    "YatraDateTime": date_time,
                    "YatraRouteId": int(request.POST.get('routeId')),
                    "YatraStatus": int(request.POST.get('status')),
                    "YatraFees": float(request.POST.get('fees')),
                    "YatraStartDateTime": date_time 
                }
                response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

            elif action == 'update_yatra':
                api_url = "https://www.lakshyapratishthan.com/apis/modifyyatra"
                yatra_id = request.POST.get('yatraId')
                if not yatra_id:
                    return JsonResponse({"message_code": 999, "message_text": "Yatra ID is required."})
                
                payload = {
                    "YatraId": int(yatra_id),
                    "YatraDateTime": date_time,
                    "YatraRouteId": int(request.POST.get('routeId')),
                    "YatraStatus": int(request.POST.get('status')),
                    "YatraFees": float(request.POST.get('fees')),
                    "YatraStartDateTime": date_time
                }
                response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
            
            else:
                return JsonResponse({"status": "error", "message": "Invalid action."})

            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({"status": "error", "message": f"API Error: {response.status_code}"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An exception occurred: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid request method."})


def logout(request):
    request.session.clear()  # Clears all session data, keeps same session key
    return redirect('login') 



# def dashboard(request):
#     """
#     Displays the dashboard with a toggleable list of yatras.
#     """
#     if 'user_id' not in request.session:
#         messages.error(request, "Please login first.")
#         return redirect('login')

#     # --- MOCK DATA (Replace with real API calls later) ---
    
#     # 1. API Call for Total Registrations
#     mock_total_registrations = 1254

#     # 2. API Call for Yatra List (this populates the initial toggles)
#     # IMPORTANT: The API for the main list should ideally include the TotalBookings count.
#     mock_yatras_list = [
#         {"YatraId": 1, "YatraRouteName": "9 Devi Pune", "YatraDateTime": "22-09-2025 08:00", "TotalBookings": 75},
#         {"YatraId": 2, "YatraRouteName": "VANI NASHIK", "YatraDateTime": "23-09-2025 09:00", "TotalBookings": 38},
#         {"YatraId": 3, "YatraRouteName": "Kondhanpur", "YatraDateTime": "24-09-2025 07:00", "TotalBookings": 112},
#         {"YatraId": 4, "YatraRouteName": "Mandhar devi", "YatraDateTime": "25-09-2025 06:00", "TotalBookings": 12},
#     ]
    
#     context = {
#         "total_registrations": mock_total_registrations,
#         "total_trips": len(mock_yatras_list),
#         "yatras": mock_yatras_list
#     }
#     # --- END OF MOCK DATA ---

#     return render(request, "dashboard.html", context)


# @csrf_exempt
# def dashboard_api(request):
#     """
#     API endpoint that returns detailed bus and seat information for a specific Yatra.
#     """
#     if 'user_id' not in request.session:
#         return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

#     if request.method == 'POST':
#         yatra_id = request.POST.get('yatra_id')
#         if not yatra_id:
#             return JsonResponse({"status": "error", "message": "Yatra ID is required."})

#         # --- MOCK DATA (This provides the details when a user clicks a toggle) ---
#         mock_trip_details = {
#             "1": {
#                 "buses": {
#                     "Bus C": {"booked_seats": list(range(1, 26))}, # 25 seats
#                     "Bus E": {"booked_seats": [1, 5, 10, 15, 20, 25, 30, 35]}, # 8 seats
#                     "Bus G": {"booked_seats": list(range(1, 36))}  # 35 seats (Full)
#                 }
#             },
#             "2": { "buses": {"Bus A": {"booked_seats": list(range(1, 16))}, "Bus B": {"booked_seats": [1, 5, 10]}} },
#             "3": { "buses": {"Bus A": {"booked_seats": list(range(1, 30))}} },
#             "4": { "buses": {} }
#         }
        
#         data_to_return = mock_trip_details.get(yatra_id, {"buses": {}})
#         # --- END OF MOCK DATA ---

#         return JsonResponse({"status": "success", "data": data_to_return})

#     return JsonResponse({"status": "error", "message": "Invalid request method."})



# @csrf_exempt
# def detailed_report_api(request):
#     """
#     API endpoint that returns a detailed list of all bookings for a specific Yatra,
#     including pilgrim contact information.
#     """
#     if 'user_id' not in request.session:
#         return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

#     if request.method == 'POST':
#         yatra_id = request.POST.get('yatra_id')
#         if not yatra_id:
#             return JsonResponse({"status": "error", "message": "Yatra ID is required."})

#         # --- MOCK DATA (Now includes Mobile and AlternateMobile numbers) ---
#         mock_booking_details = {
#             "1": {
#                 "bookings": [
#                     {"PilgrimName": "Sunil Limje", "BusName": "Bus C", "SeatNo": 1, "MobileNo": "9850180648", "AlternateMobileNo": "9999999999"},
#                     {"PilgrimName": "Amit Kumar", "BusName": "Bus C", "SeatNo": 2, "MobileNo": "9689898777", "AlternateMobileNo": ""},
#                     {"PilgrimName": "Priya Sharma", "BusName": "Bus C", "SeatNo": 3, "MobileNo": "8765432109", "AlternateMobileNo": "7654321098"},
#                     {"PilgrimName": "Rajesh Singh", "BusName": "Bus E", "SeatNo": 5, "MobileNo": "7890123456", "AlternateMobileNo": ""},
#                     {"PilgrimName": "Anjali Gupta", "BusName": "Bus E", "SeatNo": 10, "MobileNo": "8901234567", "AlternateMobileNo": ""},
#                 ]
#             },
#             "2": { "bookings": [{"PilgrimName": "Vikram Rathod", "BusName": "Bus A", "SeatNo": 1, "MobileNo": "9123456789", "AlternateMobileNo": ""}] },
#             "3": { "bookings": [{"PilgrimName": "John Doe", "BusName": "Bus A", "SeatNo": 18, "MobileNo": "9234567890", "AlternateMobileNo": ""}] },
#             "4": { "bookings": [] }
#         }
        
#         # Add more mock data for a longer list
#         if yatra_id == "1" and len(mock_booking_details["1"]["bookings"]) < 75:
#             for i in range(len(mock_booking_details["1"]["bookings"]) + 1, 76):
#                 mock_booking_details["1"]["bookings"].append(
#                     {"PilgrimName": f"Passenger {i}", "BusName": "Bus G", "SeatNo": (i % 35) + 1, "MobileNo": "9" + str(i).zfill(9), "AlternateMobileNo": ""}
#                 )
        
#         data_to_return = mock_booking_details.get(yatra_id, {"bookings": []})
#         # --- END OF MOCK DATA ---

#         return JsonResponse({"status": "success", "data": data_to_return})

#     return JsonResponse({"status": "error", "message": "Invalid request method."})




def user_master(request):
    """
    Displays the list of all users.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')
    
    api_url = "https://www.lakshyapratishthan.com/apis/listuserall"
    users = []
    try:
        response = requests.get(api_url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            users = response.json().get("message_data", [])
    except Exception as e:
        messages.error(request, f"Could not fetch user list: {e}")

    return render(request, "user_master.html", {"users": users})


@csrf_exempt
def user_master_api(request):
    """
    API to handle CRUD operations for users.
    """
    if 'user_id' not in request.session:
        return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        try:
            if action == 'add_user':
                api_url = "https://www.lakshyapratishthan.com/apis/insertuser"
                payload = {
                    "UserFirstname": request.POST.get('firstName'),
                    "UserLastname": request.POST.get('lastName'),
                    "UserMobileNo": request.POST.get('mobile'),
                    "UserLoginPin": request.POST.get('pin'),
                    "UserRoleId": int(request.POST.get('roleId'))
                }
                response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

            elif action == 'update_user':
                api_url = "https://www.lakshyapratishthan.com/apis/modifyuser"
                user_id = request.POST.get('userId')
                if not user_id:
                    return JsonResponse({"message_code": 999, "message_text": "User ID is required."})
                
                payload = {
                    "UserId": int(user_id),
                    "UserFirstname": request.POST.get('firstName'),
                    "UserLastname": request.POST.get('lastName'),
                    "UserMobileNo": request.POST.get('mobile'),
                    "UserLoginPin": request.POST.get('pin'),
                    "UserRoleId": int(request.POST.get('roleId')),
                    "UserStatus": int(request.POST.get('status'))
                }
                response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

            elif action == 'delete_user':
                api_url = "https://www.lakshyapratishthan.com/apis/deleteuser"
                user_id = request.POST.get('userId')
                if not user_id:
                    return JsonResponse({"message_code": 999, "message_text": "User ID is required."})
                
                payload = { "UserId": int(user_id) }
                response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

            else:
                return JsonResponse({"status": "error", "message": "Invalid action."})

            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({"status": "error", "message": f"API Error: {response.status_code}"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An exception occurred: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid request method."})






def dashboard(request):
    """
    Displays the dashboard, fetching real data from the APIs.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    context = {
        "total_registrations": 0,
        "total_tickets": 0, # Changed from total_trips
        "yatras": []
    }

    # 1. Fetch Total Registrations and Tickets
    try:
        totals_api_url = "https://www.lakshyapratishthan.com/apis/totals"
        response = requests.get(totals_api_url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            data = response.json().get("message_data", {})
            context["total_registrations"] = data.get("Registrations", 0)
            context["total_tickets"] = data.get("Tickets", 0) # Now using the 'Tickets' value
    except Exception as e:
        messages.error(request, f"Could not fetch totals: {e}")

    try:
        summary_api_url = "https://www.lakshyapratishthan.com/apis/totalrouteyatrabus"
        response = requests.get(summary_api_url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            summary_data = response.json().get("message_data", [])
            yatras_dict = {}
            for item in summary_data:
                yatra_id = item["YatraId"]
                if yatra_id not in yatras_dict:
                    yatras_dict[yatra_id] = { "YatraId": yatra_id, "YatraRouteName": item["YatraRouteName"], "YatraDateTime": item["YatraDateTime"], "TotalBookings": 0 }
                yatras_dict[yatra_id]["TotalBookings"] += int(item["Bookings"])
            context["yatras"] = list(yatras_dict.values())
    except Exception as e:
        messages.error(request, f"Could not fetch yatra summary: {e}")

    return render(request, "dashboard.html", context)




def dashboard(request):
    """
    Displays the dashboard, fetching real data from the APIs.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    context = {
        "total_registrations": 0,
        "total_tickets": 0, # Changed from total_trips
        "yatras": []
    }

    # 1. Fetch Total Registrations and Tickets
    try:
        totals_api_url = "https://www.lakshyapratishthan.com/apis/totals"
        response = requests.get(totals_api_url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            data = response.json().get("message_data", {})
            context["total_registrations"] = data.get("Registrations", 0)
            context["total_tickets"] = data.get("Tickets", 0) # Now using the 'Tickets' value
    except Exception as e:
        messages.error(request, f"Could not fetch totals: {e}")

    try:
        summary_api_url = "https://www.lakshyapratishthan.com/apis/totalrouteyatrabus"
        response = requests.get(summary_api_url, headers=headers, verify=False, timeout=10)
        print("1072",response.text)
        if response.status_code == 200:
            summary_data = response.json().get("message_data", [])
            yatras_dict = {}
            for item in summary_data:
                yatra_id = item["YatraId"]
                if yatra_id not in yatras_dict:
                    yatras_dict[yatra_id] = { "YatraId": yatra_id, "YatraRouteName": item["YatraRouteName"], "YatraDateTime": item["YatraDateTime"], "TotalBookings": 0 }
                yatras_dict[yatra_id]["TotalBookings"] += int(item["Bookings"])
            context["yatras"] = list(yatras_dict.values())
    except Exception as e:
        messages.error(request, f"Could not fetch yatra summary: {e}")
    print(context)
    return render(request, "dashboard.html", context)



# In views.py

@csrf_exempt
def dashboard_api(request):
    """
    API endpoint for the seat map.
    --- THIS VERSION IS NOW ACCURATE ---
    It fetches the actual list of booked seat numbers.
    """
    if 'user_id' not in request.session:
        return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

    if request.method == 'POST':
        yatra_id = request.POST.get('yatra_id')
        if not yatra_id:
            return JsonResponse({"status": "error", "message": "Yatra ID is required."})

        try:
            summary_api_url = "https://www.lakshyapratishthan.com/apis/totalrouteyatrabus"
            summary_response = requests.get(summary_api_url, headers=headers, verify=False, timeout=10)
            
            final_bus_details = {}

            if summary_response.status_code == 200:
                all_buses = summary_response.json().get("message_data", [])
                buses_for_this_yatra = [bus for bus in all_buses if bus.get("YatraId") == yatra_id]

                passenger_api_url = "https://www.lakshyapratishthan.com/apis/routeyatrabustickets"
                for bus in buses_for_this_yatra:
                    bus_name = f"Bus {bus.get('BusName', 'N/A')}"
                    payload = {
                        "YatraRouteId": bus.get("YatraRouteId"),
                        "YatraId": bus.get("YatraId"),
                        "YatraBusId": bus.get("YatraBusId")
                    }
                    
                    passenger_response = requests.post(passenger_api_url, json=payload, headers=headers, verify=False, timeout=10)
                    
                    booked_seat_numbers = [] # Start with an empty list
                    if passenger_response.status_code == 200:
                        passengers = passenger_response.json().get("message_data", [])
                        # Create a list of the ACTUAL seat numbers from the API
                        for pax in passengers:
                            try:
                                # Convert seat number string to an integer for the map
                                seat_no = int(pax.get("SeatNo"))
                                booked_seat_numbers.append(seat_no)
                            except (ValueError, TypeError):
                                continue # Ignore if SeatNo is not a valid number
                    
                    final_bus_details[bus_name] = {"booked_seats": booked_seat_numbers}

            return JsonResponse({"status": "success", "data": {"buses": final_bus_details}})

        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid request method."})




# @csrf_exempt
# def dashboard_api(request):
#     """
#     API endpoint that returns detailed bus and seat information for the seat map toggles.
#     It now correctly represents the number of booked seats.
#     """
#     if 'user_id' not in request.session:
#         return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

#     if request.method == 'POST':
#         yatra_id = request.POST.get('yatra_id')
#         if not yatra_id:
#             return JsonResponse({"status": "error", "message": "Yatra ID is required."})

#         try:
#             # --- THIS IS THE FIX ---
#             # We will use the 'totalrouteyatrabus' API which gives us the booking COUNT per bus.

#             summary_api_url = "https://www.lakshyapratishthan.com/apis/totalrouteyatrabus"
#             summary_response = requests.get(summary_api_url, headers=headers, verify=False, timeout=10)
            
#             final_bus_details = {}

#             if summary_response.status_code == 200:
#                 all_buses = summary_response.json().get("message_data", [])
                
#                 # Filter to get only the buses for the yatra we care about
#                 buses_for_this_yatra = [bus for bus in all_buses if bus.get("YatraId") == yatra_id]

#                 for bus in buses_for_this_yatra:
#                     bus_name = f"Bus {bus.get('BusName', 'N/A')}"
#                     try:
#                         booking_count = int(bus.get("Bookings", 0))
#                     except (ValueError, TypeError):
#                         booking_count = 0

#                     # Create a list of booked "seats" based on the count.
#                     # We will fill seats from 2 up to the booking_count + 1.
#                     # Example: if count is 24, it will fill seats 2, 3, ..., 25.
#                     booked_seat_numbers = list(range(3, booking_count + 3))
                    
#                     final_bus_details[bus_name] = {"booked_seats": booked_seat_numbers}

#             return JsonResponse({"status": "success", "data": {"buses": final_bus_details}})

#         except Exception as e:
#             return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"})

#     return JsonResponse({"status": "error", "message": "Invalid request method."})


@csrf_exempt
def detailed_report_api(request):
    """
    API endpoint that fetches the detailed list of passengers for the report section.
    """
    if 'user_id' not in request.session:
        return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

    if request.method == 'POST':
        yatra_id = request.POST.get('yatra_id')
        if not yatra_id:
            return JsonResponse({"status": "error", "message": "Yatra ID is required."})
        
        all_bookings = []
        try:
            summary_api_url = "https://www.lakshyapratishthan.com/apis/totalrouteyatrabus"
            summary_response = requests.get(summary_api_url, headers=headers, verify=False, timeout=10)
            buses_for_yatra = []
            if summary_response.status_code == 200:
                all_buses = summary_response.json().get("message_data", [])
                buses_for_yatra = [bus for bus in all_buses if bus.get("YatraId") == yatra_id]

            passenger_api_url = "https://www.lakshyapratishthan.com/apis/routeyatrabustickets"
            for bus in buses_for_yatra:
                payload = {
                    "YatraRouteId": bus.get("YatraRouteId"),
                    "YatraId": bus.get("YatraId"),
                    "YatraBusId": bus.get("YatraBusId")
                }
                passenger_response = requests.post(passenger_api_url, json=payload, headers=headers, verify=False, timeout=10)
                if passenger_response.status_code == 200:
                    passengers = passenger_response.json().get("message_data", [])
                    for pax in passengers:
                        first_name = pax.get("Firstname", "")
                        middle_name = pax.get("Middlename", "")
                        last_name = pax.get("Lastname", "")
                        name_parts = [part for part in [first_name, middle_name, last_name] if part]
                        full_name = " ".join(name_parts)
                        pax_details = {
                            "RegistrationId": pax.get("RegistrationId"),
                            "PilgrimName": full_name,
                            "BusName": bus.get("BusName", "N/A"),
                            "SeatNo": pax.get("SeatNo", "N/A"),
                            "MobileNo": pax.get("MobileNo", "N/A"),
                            "AlternateMobileNo": pax.get("AlternateMobileNo", "N/A")
                        }
                        all_bookings.append(pax_details)

            return JsonResponse({"status": "success", "data": {"bookings": all_bookings}})

        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An error occurred: {e}"})

    return JsonResponse({"status": "error", "message": "Invalid request method."})


@csrf_exempt
def get_pilgrim_card_api(request):
    """
    API proxy to fetch the pilgrim card image file name.
    """
    if 'user_id' not in request.session:
        return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)
    
    if request.method == 'POST':
        reg_id = request.POST.get('registration_id')
        if not reg_id or reg_id == 'null':
            return JsonResponse({"message_code": 999, "message_text": "Registration ID is invalid."})
        try:
            api_url = "https://www.lakshyapratishthan.com/apis/getpilgrimcard"
            payload = {"RegistrationId": int(reg_id)}
            
            response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

            if response.status_code == 200:
                return JsonResponse(response.json())
            else:
                return JsonResponse({"message_code": 999, "message_text": f"API Error: {response.status_code}"})
        except Exception as e:
            return JsonResponse({"message_code": 999, "message_text": f"An error occurred: {str(e)}"})

    return JsonResponse({"message_code": 999, "message_text": "Invalid request method"})


def daily_report(request):
    """
    Renders the Daily Collection Report page.
    If the user is an Admin, it also fetches the list of all users for the filter.
    """
    if 'user_id' not in request.session:
        return redirect('login')

    user_role = request.session.get("user_role")
    all_users = []

    if str(user_role) == '1':
        try:
            api_url = "https://www.lakshyapratishthan.com/apis/listuserall"
            response = requests.get(api_url, headers=headers, verify=False, timeout=10)
            if response.status_code == 200:
                all_users = response.json().get("message_data", [])
        except Exception as e:
            messages.error(request, f"Could not fetch user list: {e}")
    
    context = {
        'user_role': user_role,
        'all_users': all_users
    }
    return render(request, "daily_report.html", context)


@csrf_exempt
def daily_report_api(request):
    """
    API endpoint that fetches the booking data for a specific user and date
    using a real API call.
    """
    if 'user_id' not in request.session:
        return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

    if request.method == 'POST':
        user_id_to_fetch = request.POST.get('user_id')
        booking_date_str = request.POST.get('booking_date') 

        if not all([user_id_to_fetch, booking_date_str]):
            return JsonResponse({"status": "error", "message": "User and Date are required."})

        try:
            from datetime import datetime
            booking_date_obj = datetime.strptime(booking_date_str, "%Y-%m-%d")
            formatted_date = booking_date_obj.strftime("%d/%m/%Y")
        except ValueError:
            return JsonResponse({"status": "error", "message": "Invalid date format."})

        try:
            
            api_url = "https://www.lakshyapratishthan.com/apis/agentbookings"
            
            payload = {
                "UserId": int(user_id_to_fetch),
                "BookingDate": formatted_date
            }
            
            response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("message_code") == 1000:
                    return JsonResponse({"status": "success", "data": data.get("message_data", [])})
                else:
                    return JsonResponse({"status": "success", "data": []}) 
            else:
                return JsonResponse({"status": "error", "message": f"API Error: {response.status_code}"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid request method."})




def print_report_page(request):
    """
    Renders the dedicated page for generating the passenger list PDF.
    It now fetches all yatra data to allow for date-based filtering on the frontend.
    """
    if 'user_id' not in request.session:
        return redirect('login')

    all_yatras_summary = []

    try:
        summary_api_url = "https://www.lakshyapratishthan.com/apis/totalrouteyatrabus"
        response = requests.get(summary_api_url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            all_yatras_summary = response.json().get("message_data", [])
    except Exception as e:
        messages.error(request, f"Could not fetch yatra summary: {e}")

    return render(request, "print/print_report.html", {"all_yatras": all_yatras_summary})




def print_passenger_list(request, route_id):
    """
    Fetches passenger data for a specific route AND a specific date,
    then renders it to a downloadable PDF.
    """
    yatra_date = request.GET.get('date', None)
    if not yatra_date:
        return HttpResponse("Error: Yatra date is required.", status=400)

    try:
        route_name = "N/A"
        try:
            route_list_api_url = "https://www.lakshyapratishthan.com/apis/listrouteall"
            route_response = requests.get(route_list_api_url, headers=headers, verify=False, timeout=10)
            if route_response.status_code == 200:
                all_routes = route_response.json().get("message_data", [])
                for route in all_routes:
                    if str(route.get("YatraRouteId")) == str(route_id):
                        route_name = route.get("YatraRouteName")
                        break
        except Exception:
            pass # Continue even if this fails, will just show "N/A"

        api_url = "https://www.lakshyapratishthan.com/apis/yatrabookings"
        payload = {"YatraRouteId": route_id}
        response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
        
        if response.status_code != 200:
            return HttpResponse("Error: Could not fetch data from the API.", status=500)
            
        all_passengers = response.json().get("message_data", [])
        
        bus_filter = request.GET.get('bus', None)

        passengers_for_date = [pax for pax in all_passengers if pax.get("YatraDateTime") == yatra_date]

        if bus_filter:
            passengers_for_date = [pax for pax in passengers_for_date if pax.get("BusName") == bus_filter]

        if not passengers_for_date:
            return HttpResponse(f"No passengers found for this route on {yatra_date}.", status=404)

        buses = {}
        for pax in passengers_for_date:
            bus_name = pax.get("BusName", "Unknown Bus")
            if bus_name not in buses:
                buses[bus_name] = []
            buses[bus_name].append(pax)

        context = { 'buses': buses, 'route_name': route_name, 'yatra_date': yatra_date }

        template = get_template('print/passenger_list_pdf.html')
        html = template.render(context)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="passenger_list_route_{route_id}_{yatra_date}.pdf"'
            return response

    except Exception as e:
        return HttpResponse(f"An error occurred: {e}", status=500)

    return HttpResponse("Failed to generate PDF.", status=500)



def passenger_documents(request):
    """
    Renders the page for viewing passenger documents with filters.
    """
    if 'user_id' not in request.session:
        return redirect('login')

    routes = []
    try:
        route_list_api_url = "https://www.lakshyapratishthan.com/apis/listrouteall"
        route_response = requests.get(route_list_api_url, headers=headers, verify=False, timeout=10)
        if route_response.status_code == 200:
            all_routes = route_response.json().get("message_data", [])
            # Filter out the placeholder route with ID "0"
            routes = [route for route in all_routes if route.get("YatraRouteId") != "0"]
    except Exception as e:
        messages.error(request, f"Could not fetch routes: {e}")

    return render(request, "passenger_documents.html", {"routes": routes})



@csrf_exempt
def passenger_documents_api(request):
    """
    API for the passenger documents page with three-step filtering.
    - action 'get_filters': Fetches available Yatras and Buses for a given Route.
    - action 'get_passengers': Fetches passenger list for a specific Route, Yatra, and Bus.
    """
    if 'user_id' not in request.session:
        return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)

    action = request.POST.get('action')

    try:
        # ACTION 1: Get filter options (Yatras and Buses) for a selected Route
        if action == 'get_filters':
            route_id = request.POST.get('route_id')
            if not route_id:
                return JsonResponse({"status": "error", "message": "Route ID is required."}, status=400)

            summary_api_url = "https://www.lakshyapratishthan.com/apis/totalrouteyatrabus"
            response = requests.get(summary_api_url, headers=headers, verify=False, timeout=10)
            response.raise_for_status()

            all_yatras_summary = response.json().get("message_data", [])
            
            filters = {}
            for item in all_yatras_summary:
                if str(item.get("YatraRouteId")) == str(route_id):
                    yatra_id = item["YatraId"]
                    if yatra_id not in filters:
                        filters[yatra_id] = {
                            "date": item["YatraDateTime"],
                            "buses": []
                        }
                    filters[yatra_id]["buses"].append({
                        "id": item["YatraBusId"],
                        "name": item["BusName"]
                    })
            return JsonResponse({"status": "success", "data": filters})

        # ACTION 2: Get the detailed passenger list using the correct API
        elif action == 'get_passengers':
            route_id = request.POST.get('route_id')
            yatra_id = request.POST.get('yatra_id')
            bus_id = request.POST.get('bus_id')

            if not all([route_id, yatra_id, bus_id]):
                return JsonResponse({"status": "error", "message": "Route, Yatra, and Bus IDs are required."}, status=400)

            # THIS IS THE CORRECT API that returns all document fields
            api_url = "https://www.lakshyapratishthan.com/apis/routeyatrabustickets"
            payload = { "YatraRouteId": int(route_id), "YatraId": int(yatra_id), "YatraBusId": int(bus_id) }
            response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
            response.raise_for_status()

            passenger_data = response.json().get("message_data", [])
            return JsonResponse({"status": "success", "data": passenger_data})
        
        else:
            return JsonResponse({"status": "error", "message": "Invalid action specified."}, status=400)

    except Exception as e:
        return JsonResponse({"status": "error", "message": f"An unexpected error occurred: {e}"}, status=500)
    



def area_report(request):
    """
    Renders the page for filtering passengers by Area.
    It pre-fetches both routes and the master list of areas for the filters.
    """
    if 'user_id' not in request.session:
        return redirect('login')

    routes = []
    areas = []

    # Fetch all routes for the first filter
    try:
        route_list_api_url = "https://www.lakshyapratishthan.com/apis/listrouteall"
        response = requests.get(route_list_api_url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            all_routes = response.json().get("message_data", [])
            routes = [route for route in all_routes if route.get("YatraRouteId") != "0"]
    except Exception as e:
        messages.error(request, f"Could not fetch routes: {e}")

    # Fetch all areas for the second filter
    try:
        area_list_api_url = "https://www.lakshyapratishthan.com/apis/listarea"
        response = requests.get(area_list_api_url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            areas = response.json().get("message_data", [])
    except Exception as e:
        messages.error(request, f"Could not fetch area list: {e}")

    context = {
        "routes": routes,
        "areas": areas
    }
    return render(request, "area_report.html", context)


@csrf_exempt
def area_report_api(request):
    """
    API endpoint that fetches ALL passenger bookings for a given route.
    """
    if 'user_id' not in request.session:
        return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

    if request.method == 'POST':
        route_id = request.POST.get('route_id')
        if not route_id:
            return JsonResponse({"status": "error", "message": "Route ID is required."}, status=400)

        try:
            api_url = "https://www.lakshyapratishthan.com/apis/yatrabookings"
            payload = {"YatraRouteId": int(route_id)}
            response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
            response.raise_for_status()

            passenger_data = response.json().get("message_data", [])
            return JsonResponse({"status": "success", "data": passenger_data})

        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An error occurred: {e}"}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)


def area_report_pdf(request, route_id, area_name):
    """
    Fetches passenger data for a specific route and area,
    then renders it to a downloadable PDF.
    """
    if 'user_id' not in request.session:
        return redirect('login')

    try:
        # Fetch route name for the PDF header (optional but good for context)
        route_name = "N/A"
        try:
            route_list_api_url = "https://www.lakshyapratishthan.com/apis/listrouteall"
            route_response = requests.get(route_list_api_url, headers=headers, verify=False, timeout=10)
            if route_response.status_code == 200:
                for route in route_response.json().get("message_data", []):
                    if str(route.get("YatraRouteId")) == str(route_id):
                        route_name = route.get("YatraRouteName")
                        break
        except Exception:
            pass # Continue even if this fails

        # Fetch all passenger data for the route
        api_url = "https://www.lakshyapratishthan.com/apis/yatrabookings"
        payload = {"YatraRouteId": route_id}
        response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
        
        if response.status_code != 200:
            return HttpResponse("Error: Could not fetch passenger data from API.", status=500)
            
        all_passengers = response.json().get("message_data", [])
        
        # Filter passengers by the selected area name
        passengers_for_area = [pax for pax in all_passengers if pax.get("AreaName") == area_name]

        if not passengers_for_area:
            return HttpResponse(f"No passengers found for this area.", status=404)

        context = {
            'passengers': passengers_for_area,
            'route_name': route_name,
            'area_name': area_name,
            'total_passengers': len(passengers_for_area)
        }

        template = get_template('area_report_pdf.html')
        html = template.render(context)
        
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            safe_area_name = "".join(c for c in area_name if c.isalnum() or c in (' ', '-')).rstrip()
            response['Content-Disposition'] = f'attachment; filename="Area_Report_{route_name}_{safe_area_name}.pdf"'
            return response

    except Exception as e:
        return HttpResponse(f"An error occurred while generating the PDF: {e}", status=500)

    return HttpResponse("Failed to generate PDF.", status=500)



# In views.py

@csrf_exempt
def send_whatsapp_api(request):
    """
    API to send a WhatsApp message with detailed logging for debugging.
    """
    if 'user_id' not in request.session:
        return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

    if request.method == 'POST':
        try:
            # --- 1. Receive data from the frontend ---
            reg_id = request.POST.get('registration_id')
            user_name = request.POST.get('user_name')
            mobile_no = request.POST.get('mobile_no')
            yatra_name = request.POST.get('yatra_name')
            yatra_date = request.POST.get('yatra_date')
            bus_no = request.POST.get('bus_no')
            seat_no = request.POST.get('seat_no')
            custom_message_body = request.POST.get('custom_message_body')
            user_id = request.session.get("user_id")

            # ✅ --- ADDED FOR DEBUGGING: Print received data ---
            print("--- WhatsApp API: Data Received from Frontend ---")
            print(f"Registration ID: {reg_id}, User Name: {user_name}, Mobile: {mobile_no}")
            print(f"Yatra: {yatra_name}, Date: {yatra_date}, Bus: {bus_no}, Seat: {seat_no}")
            print("-------------------------------------------------")
            
            if not all([reg_id, mobile_no, custom_message_body, user_id]):
                return JsonResponse({"status": "error", "message": "Missing required data to send message."}, status=400)

            # --- 2. Populate placeholders ---
            final_message_body = custom_message_body.replace("{{NAME}}", user_name) \
                                                     .replace("{{YATRANAME}}", yatra_name) \
                                                     .replace("{{YATRADATE}}", yatra_date) \
                                                     .replace("{{BUSNO}}", bus_no) \
                                                     .replace("{{SEATNO}}", seat_no)

            # --- 3. Prepare payload for the external API ---
            send_api_url = "https://www.lakshyapratishthan.com/apis/addsmsrequest"
            payload = {
                "RegistrationId": int(reg_id),
                "UserId": int(user_id),
                "SMSTemplateId": 1, # Default template ID
                "SMSBody": final_message_body,
                "SMSTo": mobile_no
            }

            # ✅ --- ADDED FOR DEBUGGING: Print data being sent to external API ---
            print("--- WhatsApp API: Payload Sent to External API ---")
            import json
            print(json.dumps(payload, indent=2))
            print("--------------------------------------------------")

            # --- 4. Call the external API ---
            send_response = requests.post(send_api_url, json=payload, headers=headers, verify=False, timeout=15)
            
            # ✅ --- ADDED FOR DEBUGGING: Print response from external API ---
            print(f"--- External API Response --- (Status: {send_response.status_code})")
            try:
                print(send_response.json())
            except:
                print(send_response.text)
            print("---------------------------")


            if send_response.status_code == 200:
                response_data = send_response.json()
                if response_data.get("message_code") == 1000:
                    return JsonResponse({"status": "success", "message": "Message request sent successfully."})
                else:
                    return JsonResponse({"status": "error", "message": response_data.get("message_text", "Provider failed to send message.")})
            else:
                return JsonResponse({"status": "error", "message": f"API Error: {send_response.status_code}"})

        except Exception as e:
            print(f"[WHATSAPP API ERROR] An exception occurred: {str(e)}")
            return JsonResponse({"status": "error", "message": f"An unexpected server error occurred: {str(e)}"})

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=405)





def whatsapp_messaging_page(request):
    """
    Renders the dedicated page for sending bulk custom WhatsApp messages.
    It pre-fetches the list of routes for the initial filter.
    """
    if 'user_id' not in request.session:
        return redirect('login')

    routes = []
    try:
        route_list_api_url = "https://www.lakshyapratishthan.com/apis/listrouteall"
        route_response = requests.get(route_list_api_url, headers=headers, verify=False, timeout=10)
        if route_response.status_code == 200:
            all_routes = route_response.json().get("message_data", [])
            # Filter out the placeholder route with ID "0"
            routes = [route for route in all_routes if route.get("YatraRouteId") != "0"]
    except Exception as e:
        messages.error(request, f"Could not fetch routes: {e}")

    # The new template will be named 'whatsapp.html'
    return render(request, "whatsapp.html", {"routes": routes})




# In your views.py file, add this new function

@csrf_exempt
def get_whatsapp_templates_api(request):
    """
    A simple proxy view to fetch the list of available SMS/WhatsApp templates
    from the external API and pass them to the frontend.
    """
    if 'user_id' not in request.session:
        return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)
    
    try:
        template_api_url = "https://www.lakshyapratishthan.com/apis/listsmstemplate"
        response = requests.get(template_api_url, headers=headers, verify=False, timeout=10)

        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({"status": "error", "message": "Could not fetch templates."}, status=response.status_code)
            
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"An unexpected error occurred: {str(e)}"})





# userMobileNo:9850180648
# userPassword:999999