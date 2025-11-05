
# from collections import defaultdict
# import datetime
# from django.shortcuts import redirect, render
# from django.http import HttpResponse, JsonResponse
# import qrcode
# import requests
# from django.contrib import messages
# from django.views.decorators.csrf import csrf_exempt
# from io import BytesIO
# from django.template.loader import get_template
# from xhtml2pdf import pisa
# from PIL import Image  
# import os, uuid, json
# from django.conf import settings
# from django.http import JsonResponse
# from django.db import transaction

# from openpyxl import Workbook
# from openpyxl.styles import Font, Alignment
import datetime
from msilib.schema import Font
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
import qrcode
import json

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
                    return redirect('home')
                    # messages.success(request, data.get("message_text", "Login successful."))
                else:
                    messages.error(request, data.get("message_text", "Invalid mobile number or PIN."))
            else:
                messages.error(request, f"HTTP Error {response.status_code}")

        except Exception as e:
            print("Login Exception:", e)
            messages.error(request, "Unable to login. Please try again later.")

        return redirect('login')
    
# --- Helper to fetch dropdown data ---
def get_dropdown_data():
    areas, genders, bloodgroups = [], [], []
    try:
        # Fetch Areas
        resp_a = requests.get(f"{API_BASE_URL}listarea/", verify=False)
        if resp_a.status_code == 200 and resp_a.json().get('message_code') == 1000:
            areas = resp_a.json().get('message_data', [])
        
        # Fetch Genders
        resp_g = requests.get(f"{API_BASE_URL}listgender/", verify=False)
        if resp_g.status_code == 200 and resp_g.json().get('message_code') == 1000:
            genders = resp_g.json().get('message_data', [])
            
        # Fetch BloodGroups
        resp_b = requests.get(f"{API_BASE_URL}listbloodgroup/", verify=False)
        if resp_b.status_code == 200 and resp_b.json().get('message_code') == 1000:
            bloodgroups = resp_b.json().get('message_data', [])
            
    except Exception as e:
        print(f"Error fetching dropdown data: {e}")
    return areas, genders, bloodgroups

# --- View for NEW Registration Page ---
def new_registration_view(request):
    areas, genders, bloodgroups = get_dropdown_data()
    context = {
        'areas': areas,
        'genders': genders,
        'bloodgroups': bloodgroups
    }
    return render(request, 'yourapp/new_registration.html', context)

# --- View for UPDATE Registration Page ---
def update_registration_view(request, registration_id):
    areas, genders, bloodgroups = get_dropdown_data()
    pilgrim_data = {}
    
    # Fetch pilgrim details to pre-fill the form
    try:
        # Assuming you have an API to get details by ID. 
        # If not, you might need to use the search API or another method.
        # This is a placeholder for fetching that data.
        # Example:
        # resp = requests.post(f"{API_BASE_URL}searchregistrations/", json={'RegistrationId': registration_id}, verify=False)
        # if resp.status_code == 200 and resp.json().get('message_code') == 1000:
        #     pilgrim_data = resp.json().get('message_data', [])[0] # Assuming it returns a list
        pass # Remove this pass and add your data fetching logic
    except Exception as e:
        print(f"Error fetching pilgrim details: {e}")

    context = {
        'registration_id': registration_id,
        'pilgrim': pilgrim_data, # Pass the fetched data to the template
        'areas': areas,
        'genders': genders,
        'bloodgroups': bloodgroups
    }
    return render(request, 'yourapp/update_registration.html', context)

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
        
        elif action == "list_routes":
            api_url = f"{API_BASE_URL}listrouteall/"
            resp = requests.get(api_url, verify=False)
            return JsonResponse(resp.json(), safe=False, status=resp.status_code)

        elif action == "list_yatras":
            api_url = f"{API_BASE_URL}listyatraall/"
            resp = requests.get(api_url, verify=False)
            return JsonResponse(resp.json(), safe=False, status=resp.status_code)

        elif action == "list_buses":
            api_url = f"{API_BASE_URL}listroutebus/"
            resp = requests.get(api_url, verify=False)
            return JsonResponse(resp.json(), safe=False, status=resp.status_code)
        
        elif action == "fetch_seats":
            try:
                # 1. The URL of your independent backend API
                api_url = f"{API_BASE_URL}fetch_bus_seats/"

                # 2. Get parameters from the frontend's request to this proxy
                route_id = request.POST.get('route_id')
                yatra_id = request.POST.get('yatra_id')
                bus_id = request.POST.get('bus_id')

                # 3. Prepare the JSON payload to send to the independent API
                payload = {
                    "route_id": int(route_id),
                    "yatra_id": int(yatra_id),
                    "bus_id": int(bus_id)
                }
                # ✅ CORRECTED THIS LINE
                response = requests.post(api_url, json=payload)

                # 5. Check the response and pass it through to the frontend
                response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
                
                # Return the exact JSON from the independent API back to the browser
                return JsonResponse(response.json())

            except requests.exceptions.HTTPError as e:
                # If the backend API returned an error (e.g., 404, 500)
                return JsonResponse({
                    "message_code": 995,
                    "message_text": f"Backend service error: {e.response.status_code}",
                    "details": e.response.text
                }, status=502) # Bad Gateway
            except requests.exceptions.RequestException as e:
                # Handle network errors (e.g., the backend API is down)
                return JsonResponse({
                    "message_code": 994,
                    "message_text": f"Could not connect to the booking service: {e}"
                }, status=503) # Service Unavailable
        
        elif action == "book_ticket":
            try:
                # --- 1. GATHER ALL PARAMETERS FROM THE FRONTEND REQUEST ---
                user_id = request.POST.get("UserId")
                amount_paid = request.POST.get("AmountPaid", "0")
                discount = request.POST.get("Discount", "0")
                discount_reason = request.POST.get("DiscountReason", "")
                payment_mode_raw = request.POST.get("PaymentMode", "cash").lower()
                
                # This is the critical part: Get the JSON string from the frontend
                bookings_json_string = request.POST.get("Bookings", "[]")
                
                # --- 2. CONSTRUCT THE PAYLOAD EXACTLY AS THE EXTERNAL API REQUIRES ---
                
                # Convert the received JSON string into a Python object
                bookings_data = json.loads(bookings_json_string)

                # Convert payment mode name to the required integer ID
                payment_mode_id = 1  # Default to Cash
                if payment_mode_raw == "upi":
                    payment_mode_id = 2

                # Build the final payload for the single API call
                api_payload = {
                    "UserId": user_id,
                    "AmountPaid": amount_paid,
                    "Discount": discount,
                    "DiscountReason": discount_reason,
                    "PaymentMode": payment_mode_id,
                    "Bookings": bookings_data  # Embed the parsed booking data directly
                }

                # --- 3. SEND THE SINGLE, CORRECTLY FORMATTED REQUEST TO THE EXTERNAL API ---
                
                api_url = f"{API_BASE_URL}inserttickets/"
                
                print("✅ Final Payload being sent to External API:", json.dumps(api_payload, indent=2))

                response = requests.post(api_url, json=api_payload, verify=False)
                response.raise_for_status()  # Raise an error for bad status codes (4xx or 5xx)
                
                api_response_data = response.json()
                print("✅ Response Received from External API:", api_response_data)
                
                # --- 4. RETURN THE API'S RESPONSE TO THE FRONTEND ---
                
                # Check the message_code from the external API's response
                if str(api_response_data.get("message_code")) == "1000":
                    return JsonResponse({
                        "message_code": 1000,
                        "message_text": api_response_data.get("message_text", "Tickets booked successfully."),
                        "message_data": api_response_data.get("message_data", {})
                    })
                else:
                    # Pass through the error from the external API to the frontend
                    return JsonResponse({
                        "message_code": 998,
                        "message_text": api_response_data.get("message_text", "An error occurred during booking.")
                    }, status=400)

            except json.JSONDecodeError:
                return JsonResponse({
                    "message_code": 997,
                    "message_text": "Invalid JSON format received from frontend for 'Bookings'."
                }, status=400)
            except requests.exceptions.RequestException as e:
                return JsonResponse({
                    "message_code": 996,
                    "message_text": f"Could not connect to the booking service: {str(e)}"
                }, status=503)
            except Exception as e:
                return JsonResponse({
                    "message_code": 999,
                    "message_text": f"An unexpected server error occurred: {str(e)}"
                }, status=500)
            
        elif action == "check_booked_tickets":
            try:
                # Get the JSON string of registration IDs from the frontend
                reg_ids_json = request.POST.get("regids", "[]")
                
                # Convert the JSON string into a Python list
                reg_ids_list = json.loads(reg_ids_json)

                # The URL of your external API endpoint
                api_url = f"{API_BASE_URL}CheckTicketsForReg/" # Make sure this URL is correct

                # The payload the external API is expecting
                payload = {"regids": reg_ids_list}
                
                # Make the request to the external API
                response = requests.post(api_url, json=payload, verify=False)
                response.raise_for_status() # Raise an exception for bad status codes

                # Return the external API's response directly to the frontend
                return JsonResponse(response.json())

            except json.JSONDecodeError:
                return JsonResponse({"message_code": 997, "message_text": "Invalid format for registration IDs."}, status=400)
            except requests.exceptions.RequestException as e:
                return JsonResponse({"message_code": 996, "message_text": f"Could not connect to the booking history service: {str(e)}"}, status=503)
  

        elif action == "get_pilgrim_card":
            try:
                registration_id = request.POST.get("RegistrationId")
                if not registration_id:
                    return JsonResponse({"message_code": 998, "message_text": "Registration ID is required."}, status=400)

                # Construct the full URL to the external API endpoint
                api_url = f"{API_BASE_URL}getpilgrimcard/" 
                payload = {"RegistrationId": registration_id}
                
                # Call the external API
                response = requests.post(api_url, json=payload, verify=False)
                response.raise_for_status()

                # --- START: CORRECT URL CONSTRUCTION ---
                response_data = response.json()

                # Check if the API call was successful
                if response_data.get('message_code') == 1000 and response_data.get('message_data'):
                    # This is the partial path from the API: "/LakshyaPratishthan/media/cards/18.png"
                    partial_path = response_data['message_data']  

                    # Let's dynamically and safely extract the domain from your existing constant
                    from urllib.parse import urlparse
                    
                    # urlparse("http://127.0.0.1:8000/LakshyaPratishthan/api/")
                    parsed_base = urlparse(API_BASE_URL) 
                    
                    # This will correctly result in "http://127.0.0.1:8000"
                    api_domain = f"{parsed_base.scheme}://{parsed_base.netloc}" 
                    
                    # This creates the final, correct URL:
                    # "http://127.0.0.1:8000" + "/LakshyaPratishthan/media/cards/18.png"
                    full_url = f"{api_domain}{partial_path}"
                    
                    # Update the response data with the full URL before sending it to the frontend
                    response_data['message_data'] = full_url

                # Return the modified JSON with the full URL to the frontend
                return JsonResponse(response_data)
                # --- END: CORRECT URL CONSTRUCTION ---

            except requests.exceptions.RequestException as e:
                return JsonResponse({"message_code": 996, "message_text": f"Could not connect to the card generation service: {str(e)}"}, status=503)

        elif action == "cancel_ticket":
            try:
                registration_id = request.POST.get("RegistrationId")
                if not registration_id:
                    return JsonResponse({"message_code": 998, "message_text": "Registration ID is required for cancellation."}, status=400)

                # Call the internal cancelticket API endpoint
                api_url = f"{API_BASE_URL}cancelticket/" 
                payload = {"RegistrationId": registration_id}
                
                print(f"✅ Sending cancellation request to API: {api_url} with payload: {payload}")
                response = requests.post(api_url, json=payload, verify=False)
                response.raise_for_status() # Raise an exception for bad status codes

                api_response_data = response.json()
                print(f"✅ Cancellation API response: {api_response_data}")
                
                if str(api_response_data.get("message_code")) == "1000":
                    return JsonResponse({
                        "message_code": 1000,
                        "message_text": api_response_data.get("message_text", "Tickets cancelled successfully."),
                        "message_data": api_response_data.get("message_data", {})
                    })
                else:
                    return JsonResponse({
                        "message_code": 998,
                        "message_text": api_response_data.get("message_text", "An error occurred during cancellation.")
                    }, status=400)

            except requests.exceptions.RequestException as e:
                return JsonResponse({
                    "message_code": 996,
                    "message_text": f"Could not connect to the cancellation service: {str(e)}"
                }, status=503)
            except Exception as e:
                return JsonResponse({
                    "message_code": 999,
                    "message_text": f"An unexpected server error occurred during cancellation: {str(e)}"
                }, status=500)        
            
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
                        aadhar_url = f"http://127.0.0.1:8001/Yatra_darshan/static/assets/adhar/{file_name}.pdf"
                    else:
                        save_path = os.path.join(img_directory, f"{file_name}.png")
                        image = Image.open(aadhar_file)
                        image = image.convert("RGB")
                        image.save(save_path, "PNG")
                        aadhar_url = f"http://127.0.0.1:8001/Yatra_darshan/static/assets/adhar/{file_name}.png"

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
                        profile_url = f"http://127.0.0.1:8001/Yatra_darshan/static/assets/profile/{file_name}.pdf"
                    else:
                        save_path = os.path.join(img_directory, f"{file_name}.png")
                        image = Image.open(profile_file)
                        image = image.convert("RGB")
                        image.save(save_path, "PNG")
                        profile_url = f"http://127.0.0.1:8001/Yatra_darshan/static/assets/profile/{file_name}.png"

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
                        voterId_url = f"http://127.0.0.1:8001/Yatra_darshan/static/assets/voterId/{file_name}.pdf"
                    else:
                        save_path = os.path.join(img_directory, f"{file_name}.png")
                        image = Image.open(voterId_File)
                        image = image.convert("RGB")
                        image.save(save_path, "PNG")
                        voterId_url = f"http://127.0.0.1:8001/Yatra_darshan/static/assets/voterId/{file_name}.png"
                
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
    

# def TicketBooking(request):
#     """
#     Renders the main Yatra Darshan Booking page.
#     """
#     if 'user_id' not in request.session:
#         messages.error(request, "Please login first.")
#         return redirect('login')
#     return render(request, 'TicketBooking.html')

# @csrf_exempt
# def TicketBookingApi(request):
#     """
#     Handles all API requests from the booking page frontend.
#     """
#     if 'user_id' not in request.session:
#         return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

#     if request.method == 'POST':
#         action = request.POST.get('action')
#         try:
#             # ✅ Search registrations
#             if action == 'search_registrations':
#                 mobile_no = request.POST.get('MobileNo', '')
#                 if not mobile_no:
#                     return JsonResponse({"message_code": 999, "message_text": "Mobile number is required."})
                
#                 api_url = f"{API_BASE_URL}searchregistrations/"
#                 payload = {"MobileNo": mobile_no}
#                 response = requests.post(api_url, json=payload, verify=False, timeout=15)
#                 return JsonResponse(response.json(), status=response.status_code)

#             # ✅ Load dropdowns
#             elif action == 'load_dropdowns':
#                 dropdown_type = request.POST.get('dropdown_type')
#                 if dropdown_type == 'gender':
#                     api_url = f"{API_BASE_URL}listgender/"
#                 elif dropdown_type == 'area':
#                     api_url = f"{API_BASE_URL}listarea/"
#                 elif dropdown_type == 'bloodgroup':
#                     api_url = f"{API_BASE_URL}listbloodgroup/"
#                 else:
#                     return JsonResponse({"message_code": 999, "message_text": "Invalid dropdown type."})

#                 response = requests.get(api_url, verify=False, timeout=15)
#                 return JsonResponse(response.json(), status=response.status_code)

#             # ✅ Add or Update registration (same API with RegistrationId)
#             elif action in ['add_registration', 'update_registration']:
#                 payload = {
#                     "userMobileNo": request.POST.get('MobileNo'),
#                     "userAlternateMobileNo": request.POST.get('AlternateMobileNo'),
#                     "userFirstname": request.POST.get('Firstname'),
#                     "userMiddlename": request.POST.get('Middlename'),
#                     "userLastname": request.POST.get('Lastname'),
#                     "Address": request.POST.get('Address'),
#                     "AreaId": request.POST.get('AreaId'),
#                     "Gender": request.POST.get('Gender'),
#                     "BloodGroup": request.POST.get('BloodGroup'),
#                     "DateOfBirth": request.POST.get('DateOfBirth'),
#                     "AadharNumber": request.POST.get('AadharNumber'),
#                     "UserId": request.session.get('user_id', 1),
#                     "Photo": request.POST.get('Photo'),
#                     "PhotoId": request.POST.get('PhotoId'),
#                     "VoterId": request.POST.get('VoterId'),
#                     "PhotoFileName": request.POST.get('PhotoFileName'),
#                     "IdProofFileName": request.POST.get('IdProofFileName'),
#                 }

#                 # Include RegistrationId only for update
#                 if action == 'update_registration':
#                     reg_id = request.POST.get('RegistrationId')
#                     if not reg_id:
#                         return JsonResponse({"message_code": 999, "message_text": "Registration ID required."})
#                     payload["RegistrationId"] = reg_id

#                 api_url = f"{API_BASE_URL}pilgrimregistration/"
#                 response = requests.post(api_url, json=payload, verify=False, timeout=15)
#                 return JsonResponse(response.json(), status=response.status_code)

#             else:
#                 return JsonResponse({"status": "error", "message": "Invalid action specified."})

#         except Exception as e:
#             return JsonResponse({"status": "error", "message": str(e)}, status=500)

#     return JsonResponse({"status": "error", "message": "Invalid request method."})


def route_master(request):
    """
    Displays the list of all Yatra routes.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')
    
    # CHANGED: Using the new API endpoint
    api_url = f"{API_BASE_URL}listrouteall/" 
    
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
                # CHANGED: Using the new API endpoint for inserting a route
                api_url = f"{API_BASE_URL}insertroute/"
                payload = {
                    "YatraRouteName": request.POST.get('routeName'),
                    "YatraRouteDetails": request.POST.get('routeDetails'),
                    "YatraRouteStatus": int(request.POST.get('status')) 
                }
                # Your new API uses POST for creation, so this stays the same
                response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

            elif action == 'update_route':
                route_id = request.POST.get('routeId')
                if not route_id:
                    return JsonResponse({
                        "message_code": 999,
                        "message_text": "Error: Route ID was not provided for the update."
                    })

                # CHANGED: Using the new API endpoint for modifying a route
                api_url = f"{API_BASE_URL}modifyroute/"
                payload = {
                    "YatraRouteId": int(route_id),
                    "YatraRouteName": request.POST.get('routeName'),
                    "YatraRouteDetails": request.POST.get('routeDetails'),
                    "YatraRouteStatus": int(request.POST.get('status'))
                }

                response = requests.put(api_url, json=payload, headers=headers, verify=False, timeout=10)
            
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
    
    # CHANGED: Using the new API endpoint
    api_url = f"{API_BASE_URL}listareaall/"
    
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
                # CHANGED: Using the new API endpoint
                api_url = f"{API_BASE_URL}insertarea/"
                payload = {
                    "AreaName": request.POST.get('areaName'),
                }
                response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

            elif action == 'update_area':
                # CHANGED: Using the new API endpoint
                api_url = f"{API_BASE_URL}modifyarea/"
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
        # CHANGED: Using the new API endpoint for Yatras
        yatra_api_url = f"{API_BASE_URL}listyatraall/"
        response = requests.get(yatra_api_url, headers=headers, verify=False, timeout=10)
        if response.status_code == 200:
            yatras = response.json().get("message_data", [])
    except Exception as e:
        messages.error(request, f"Could not fetch Yatra list: {e}")
    try:
        # CHANGED: Using the new API endpoint for Routes
        route_api_url = f"{API_BASE_URL}listrouteall/"
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
            # The date format from the frontend is likely 'YYYY-MM-DDTHH:mm'
            # The new API expects 'DD-MM-YYYY HH:MM'
            # We must convert it.
            date_time_raw = request.POST.get('dateTime')
            from datetime import datetime
            date_time_obj = datetime.strptime(date_time_raw, "%Y-%m-%dT%H:%M")
            date_time_formatted = date_time_obj.strftime("%d-%m-%Y %H:%M")

            if action == 'add_yatra':
                # CHANGED: Using the new API endpoint
                api_url = f"{API_BASE_URL}insertyatra/"
                payload = {
                    "YatraDateTime": date_time_formatted,
                    "YatraRouteId": int(request.POST.get('routeId')),
                    "YatraStatus": int(request.POST.get('status')),
                    "YatraFees": float(request.POST.get('fees')),
                    "YatraStartDateTime": date_time_formatted # Assuming start time is same as yatra time
                }
                response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

            elif action == 'update_yatra':
                # CHANGED: Using the new API endpoint
                api_url = f"{API_BASE_URL}modifyyatra/"
                yatra_id = request.POST.get('yatraId')
                if not yatra_id:
                    return JsonResponse({"message_code": 999, "message_text": "Yatra ID is required."})
                
                payload = {
                    "YatraId": int(yatra_id),
                    "YatraDateTime": date_time_formatted,
                    "YatraRouteId": int(request.POST.get('routeId')),
                    "YatraStatus": int(request.POST.get('status')),
                    "YatraFees": float(request.POST.get('fees')),
                    "YatraStartDateTime": date_time_formatted
                }
                # This will be a POST request, matching our API change below
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


# def yatra_bus_master(request):
#     """
#     Displays the list of all Yatra buses and fetches related data for dropdowns.
#     """
#     if 'user_id' not in request.session:
#         messages.error(request, "Please login first.")
#         return redirect('login')

#     buses = []
#     yatras = []
#     routes = []
    
#     # Fetch Yatra Buses
#     try:
#         response = requests.get(f"{API_BASE_URL}listyatrabuses/", verify=False, timeout=15)
#         if response.status_code == 200 and response.json().get("message_code") == 1000:
#             buses = response.json().get("message_data", [])
#         else:
#             messages.error(request, f"Could not fetch bus list: {response.json().get('message_text', 'Unknown API error.')}")
#     except Exception as e:
#         messages.error(request, f"Could not fetch bus list. A network error occurred: {e}")

#     # Fetch all Yatras for the dropdown
#     try:
#         response = requests.get(f"{API_BASE_URL}listyatra/", verify=False, timeout=15)
#         if response.status_code == 200 and response.json().get("message_code") == 1000:
#             yatras = response.json().get("message_data", [])
#     except Exception as e:
#         messages.error(request, f"Could not fetch Yatra list for dropdowns: {e}")

#     # Fetch all Routes for the dropdown
#     try:
#         response = requests.get(f"{API_BASE_URL}listrouteall/", verify=False, timeout=15)
#         if response.status_code == 200 and response.json().get("message_code") == 1000:
#             routes = response.json().get("message_data", [])
#     except Exception as e:
#         messages.error(request, f"Could not fetch Route list for dropdowns: {e}")

#     context = {
#         "buses": buses,
#         "yatras": yatras,
#         "routes": routes
#     }
#     return render(request, "yatra_bus_master.html", context)


# @csrf_exempt
# def yatra_bus_master_api(request):
#     """
#     API to handle CRUD operations for Yatra Buses.
#     (This function remains unchanged as the logic was already correct)
#     """
#     if 'user_id' not in request.session:
#         return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

#     if request.method == 'POST':
#         action = request.POST.get('action')
        
#         try:
#             # Shared payload for Add/Update
#             payload = {
#                 "BusName": request.POST.get('BusName'),
#                 "BusDateTimeStart": request.POST.get('BusDateTimeStart'),
#                 "SeatFees": request.POST.get('SeatFees'),
#                 "YatraRouteId": request.POST.get('YatraRouteId'),
#                 "YatraId": request.POST.get('YatraId'),
#                 "BusCapacity": request.POST.get('BusCapacity'),
#                 "ReservedSeats": request.POST.get('ReservedSeats', '1,2'),
#                 "UserId": request.session.get('user_id', 1) # Get user from session
#             }

#             if action == 'add_yatra_bus':
#                 api_url = f"{API_BASE_URL}createyatrabus/"
#                 response = requests.post(api_url, json=payload, verify=False, timeout=15)

#             elif action == 'update_yatra_bus':
#                 api_url = f"{API_BASE_URL}modifyyatrabus/"
#                 yatra_bus_id = request.POST.get('YatraBusId')
#                 if not yatra_bus_id:
#                     return JsonResponse({"message_code": 999, "message_text": "Yatra Bus ID is required for updates."})
                
#                 payload["YatraBusId"] = int(yatra_bus_id)
#                 response = requests.post(api_url, json=payload, verify=False, timeout=15)

#             elif action == 'delete_yatra_bus':
#                 api_url = f"{API_BASE_URL}deleteyatrabus/"
#                 yatra_bus_id = request.POST.get('YatraBusId')
#                 if not yatra_bus_id:
#                     return JsonResponse({"message_code": 999, "message_text": "Yatra Bus ID is required for deletion."})
                
#                 delete_payload = { 
#                     "YatraBusId": int(yatra_bus_id),
#                     "UserId": request.session.get('user_id', 1)
#                 }
#                 response = requests.post(api_url, json=delete_payload, verify=False, timeout=15)

#             else:
#                 return JsonResponse({"status": "error", "message": "Invalid action."})

#             # Return the JSON response from the downstream API directly to the frontend
#             return JsonResponse(response.json(), status=response.status_code)

#         except requests.exceptions.RequestException as e:
#             return JsonResponse({"status": "error", "message": f"A network error occurred: {str(e)}"})
#         except Exception as e:
#             return JsonResponse({"status": "error", "message": f"An unexpected error occurred: {str(e)}"})

#     return JsonResponse({"status": "error", "message": "Invalid request method."})

def yatra_bus_master(request):
    """
    Displays a grouped accordion list of Yatra buses and fetches data for the modal.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    buses = []
    yatras = []
    routes = []
    
    # Fetch all necessary data
    try:
        buses_response = requests.get(f"{API_BASE_URL}listyatrabuses/", verify=False, timeout=15)
        if buses_response.json().get("message_code") == 1000:
            buses = buses_response.json().get("message_data", [])
    except Exception as e:
        messages.error(request, f"Could not fetch bus list: {e}")

    try:
        yatras_response = requests.get(f"{API_BASE_URL}listyatra/", verify=False, timeout=15)
        if yatras_response.json().get("message_code") == 1000:
            yatras = yatras_response.json().get("message_data", [])
    except Exception as e:
        messages.error(request, f"Could not fetch Yatra list: {e}")

    try:
        routes_response = requests.get(f"{API_BASE_URL}listrouteall/", verify=False, timeout=15)
        # Note: The provided API response for listrouteall seems incorrect. 
        # We will derive unique routes from the buses list as a reliable alternative.
        if routes_response.json().get("message_code") == 1000:
            # Create a unique list of routes from the response
            temp_routes = {}
            for route_data in routes_response.json().get("message_data", []):
                temp_routes[route_data['YatraRouteId']] = {
                    "YatraRouteId": route_data['YatraRouteId'],
                    "YatraRouteName": route_data['YatraRouteName']
                }
            routes = list(temp_routes.values())
    except Exception as e:
        messages.error(request, f"Could not fetch Route list: {e}")
        
    # --- New Logic: Group buses into a structured list for the accordion ---
    structured_routes = []
    route_map = {}
    
    # Sort buses by Route Name and then Yatra Date for ordered display
    sorted_buses = sorted(buses, key=lambda x: (x.get('YatraRouteName', ''), x.get('YatraDateTime', '')))

    for bus in sorted_buses:
        route_id = bus.get('YatraRouteId')
        route_name = bus.get('YatraRouteName', 'Uncategorized')
        yatra_id = bus.get('YatraId')

        # If we haven't processed this route yet, create its main entry
        if route_id not in route_map:
            route_entry = {
                'YatraRouteName': route_name,
                'YatraRouteId': route_id,
                'yatras': {}  # Use a dictionary to group buses by yatra
            }
            route_map[route_id] = route_entry
            structured_routes.append(route_entry)

        # If this yatra is new for this route, create its entry
        if yatra_id not in route_map[route_id]['yatras']:
            route_map[route_id]['yatras'][yatra_id] = {
                'details': { 'YatraDateTime': bus.get('YatraDateTime'), 'YatraId': yatra_id },
                'buses': []
            }
        
        # Add the bus to its corresponding yatra
        route_map[route_id]['yatras'][yatra_id]['buses'].append(bus)

    # Convert the inner yatra dictionary to a list for easier looping in the template
    for route in structured_routes:
        route['yatras'] = list(route['yatras'].values())

    context = {
        "structured_routes": structured_routes,
        "all_yatras_for_modal": yatras,
        "all_routes_for_modal": routes
    }
    return render(request, "yatra_bus_master.html", context)


@csrf_exempt
def yatra_bus_master_api(request):
    """
    API to handle CRUD operations for Yatra Buses. (This logic remains correct).
    """
    if 'user_id' not in request.session:
        return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)
    if request.method == 'POST':
        action = request.POST.get('action')
        try:
            payload = {
                "BusName": request.POST.get('BusName'),
                "BusDateTimeStart": request.POST.get('BusDateTimeStart'),
                "SeatFees": request.POST.get('SeatFees'),
                "YatraRouteId": request.POST.get('YatraRouteId'),
                "YatraId": request.POST.get('YatraId'),
                "BusCapacity": request.POST.get('BusCapacity'),
                "ReservedSeats": request.POST.get('ReservedSeats', '1,2'),
                "UserId": request.session.get('user_id', 1)
            }
            if action == 'add_yatra_bus':
                response = requests.post(f"{API_BASE_URL}createyatrabus/", json=payload, verify=False)
            elif action == 'update_yatra_bus':
                payload["YatraBusId"] = int(request.POST.get('YatraBusId'))
                response = requests.post(f"{API_BASE_URL}modifyyatrabus/", json=payload, verify=False)
            elif action == 'delete_yatra_bus':
                delete_payload = {"YatraBusId": int(request.POST.get('YatraBusId')), "UserId": request.session.get('user_id', 1)}
                response = requests.post(f"{API_BASE_URL}deleteyatrabus/", json=delete_payload, verify=False)
            else:
                return JsonResponse({"status": "error", "message": "Invalid action."})
            return JsonResponse(response.json(), status=response.status_code)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"})
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
    
    # api_url = "https://www.lakshyapratishthan.com/apis/listuserall"
    api_url = f"{API_BASE_URL}listuserall/"
    users = []
    try:
        # response = requests.get(api_url, headers=headers, verify=False, timeout=10)
        response = requests.get(api_url,verify=False)
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
                # api_url = "https://www.lakshyapratishthan.com/apis/insertuser"
                api_url = f"{API_BASE_URL}insertuser/"
                payload = {
                    "UserFirstname": request.POST.get('firstName'),
                    "UserLastname": request.POST.get('lastName'),
                    "UserMobileNo": request.POST.get('mobile'),
                    "UserLoginPin": request.POST.get('pin'),
                    "UserRoleId": int(request.POST.get('roleId'))
                }
                # response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
                response = requests.post(api_url,json=payload,verify=False)

            elif action == 'update_user':
                # api_url = "https://www.lakshyapratishthan.com/apis/modifyuser"
                api_url = f"{API_BASE_URL}modifyuser/"
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
                # response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
                response = requests.post(api_url,json=payload,verify=False)

            elif action == 'delete_user':
                # api_url = "https://www.lakshyapratishthan.com/apis/deleteuser"
                api_url = f"{API_BASE_URL}deleteuser/"
                user_id = request.POST.get('userId')
                if not user_id:
                    return JsonResponse({"message_code": 999, "message_text": "User ID is required."})
                
                payload = { "UserId": int(user_id) }
                # response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
                response = requests.post(api_url, json=payload,verify=False)

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
        # totals_api_url = "https://www.lakshyapratishthan.com/apis/totals"
        totals_api_url = f"{API_BASE_URL}totals/"
        # response = requests.get(totals_api_url, headers=headers, verify=False, timeout=10)
        response = requests.get(totals_api_url, verify=False)
        if response.status_code == 200:
            data = response.json().get("message_data", {})
            context["total_registrations"] = data.get("Registrations", 0)
            context["total_tickets"] = data.get("Tickets", 0) # Now using the 'Tickets' value
    except Exception as e:
        messages.error(request, f"Could not fetch totals: {e}")

    try:
        # summary_api_url = "https://www.lakshyapratishthan.com/apis/totalrouteyatrabus"
        summary_api_url = f"{API_BASE_URL}totalrouteyatrabus/"
        # response = requests.get(summary_api_url, headers=headers, verify=False, timeout=10)
        response = requests.get(summary_api_url, verify=False)
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
            # summary_api_url = "https://www.lakshyapratishthan.com/apis/totalrouteyatrabus"
            summary_api_url = f"{API_BASE_URL}totalrouteyatrabus/"
            # summary_response = requests.get(summary_api_url, headers=headers, verify=False, timeout=10)
            summary_response = requests.get(summary_api_url,verify=False)
            final_bus_details = {}

            if summary_response.status_code == 200:
                all_buses = summary_response.json().get("message_data", [])
                buses_for_this_yatra = [bus for bus in all_buses if bus.get("YatraId") == yatra_id]

                # passenger_api_url = "https://www.lakshyapratishthan.com/apis/routeyatrabustickets"
                passenger_api_url = f"{API_BASE_URL}routeyatrabustickets/"
                for bus in buses_for_this_yatra:
                    bus_name = f"Bus {bus.get('BusName', 'N/A')}"
                    payload = {
                        "YatraRouteId": bus.get("YatraRouteId"),
                        "YatraId": bus.get("YatraId"),
                        "YatraBusId": bus.get("YatraBusId")
                    }
                    
                    # passenger_response = requests.post(passenger_api_url, json=payload, headers=headers, verify=False, timeout=10)
                    passenger_response = requests.post(passenger_api_url, json=payload,verify=False)
                    
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


@csrf_exempt
def detailed_report_api(request):
    """
    NEW: API endpoint for the Detailed Booking Report.
    Fetches all passenger details for a given Yatra.
    """
    if 'user_id' not in request.session:
        return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

    yatra_id_str = request.POST.get('yatra_id')
    if not yatra_id_str:
        return JsonResponse({"status": "error", "message": "Yatra ID is required."})

    try:
        yatra_id = int(yatra_id_str)
        # summary_api_url = f"{API_BASE_URL}totalrouteyatrabus/"
        summary_api_url = f"{API_BASE_URL}totalrouteyatrabus/"
        # summary_response = requests.get(summary_api_url, verify=False, timeout=15)
        summary_response = requests.get(summary_api_url,verify=False)
        all_bookings = []

        if summary_response.status_code == 200:
            all_buses = summary_response.json().get("message_data", [])
            buses_for_this_yatra = [bus for bus in all_buses if bus.get("YatraId") == yatra_id]
            
            passenger_api_url = f"{API_BASE_URL}routeyatrabustickets/"
            for bus in buses_for_this_yatra:
                payload = {
                    "YatraRouteId": bus.get("YatraRouteId"),
                    "YatraId": bus.get("YatraId"),
                    "YatraBusId": bus.get("YatraBusId")
                }
                passenger_response = requests.post(passenger_api_url, json=payload, verify=False, timeout=15)
                
                if passenger_response.status_code == 200:
                    passengers = passenger_response.json().get("message_data", [])
                    # Add the bus name to each passenger record for easy grouping in the frontend
                    for pax in passengers:
                        pax['BusName'] = f"Bus {bus.get('BusName', 'N/A')}"
                    all_bookings.extend(passengers)
        
        return JsonResponse({"status": "success", "data": {"bookings": all_bookings}})
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"})


@csrf_exempt
def get_pilgrim_card_api(request):
    """
    NEW: API endpoint to fetch the pilgrim card image path for printing.
    Acts as a proxy to your backend service.
    """
    if 'user_id' not in request.session:
        return JsonResponse({"status": "error", "message": "Authentication required."}, status=401)

    registration_id = request.POST.get('registration_id')
    if not registration_id:
        return JsonResponse({"message_code": 999, "message_text": "Registration ID is required."})

    try:
        # Assuming the backend API endpoint is named 'getpilgrimcard'
        api_url = f"{API_BASE_URL}getpilgrimcard/"
        payload = {"RegistrationId": registration_id}
        response = requests.post(api_url, json=payload, verify=False, timeout=15)
        return JsonResponse(response.json())
    except Exception as e:
        return JsonResponse({"message_code": 999, "message_text": f"An error occurred: {str(e)}"})

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
            # api_url = "https://www.lakshyapratishthan.com/apis/listuserall"
            api_url = f"{API_BASE_URL}listuserall/"
            # response = requests.get(api_url, headers=headers, verify=False, timeout=10)
            response = requests.get(api_url, verify=False, )
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
            
            # api_url = "https://www.lakshyapratishthan.com/apis/agentbookings"
            api_url = f"{API_BASE_URL}agentbookings/"
            
            payload = {
                "UserId": int(user_id_to_fetch),
                "BookingDate": formatted_date
            }
            
            # response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
            response = requests.post(api_url,json=payload, verify=False, )

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
        # summary_api_url = "https://www.lakshyapratishthan.com/apis/totalrouteyatrabus"
        summary_api_url = f"{API_BASE_URL}totalrouteyatrabus/"
        # response = requests.get(summary_api_url, headers=headers, verify=False, timeout=10)
        response = requests.get(summary_api_url)
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
            # route_list_api_url = "https://www.lakshyapratishthan.com/apis/listrouteall"
            route_list_api_url = f"{API_BASE_URL}listrouteall/"
            route_response = requests.get(route_list_api_url, verify=False)
            if route_response.status_code == 200:
                all_routes = route_response.json().get("message_data", [])
                for route in all_routes:
                    if str(route.get("YatraRouteId")) == str(route_id):
                        route_name = route.get("YatraRouteName")
                        break
        except Exception:
            pass # Continue even if this fails, will just show "N/A"

        # api_url = "https://www.lakshyapratishthan.com/apis/yatrabookings"
        api_url = f"{API_BASE_URL}yatrabookings/"
        payload = {"YatraRouteId": route_id}
        # response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
        response = requests.post(api_url,json=payload)
        
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
        # route_list_api_url = "https://www.lakshyapratishthan.com/apis/listrouteall"
        route_list_api_url = f"{API_BASE_URL}listrouteall/"
        # route_response = requests.get(route_list_api_url, headers=headers, verify=False, timeout=10)
        route_response = requests.get(route_list_api_url)
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

            # summary_api_url = "https://www.lakshyapratishthan.com/apis/totalrouteyatrabus"
            summary_api_url = f"{API_BASE_URL}totalrouteyatrabus/"
            # response = requests.get(summary_api_url, headers=headers, verify=False, timeout=10)
            response = requests.get(summary_api_url ,verify=False)
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
            # api_url = "https://www.lakshyapratishthan.com/apis/routeyatrabustickets"
            api_url = f"{API_BASE_URL}routeyatrabustickets/"
            payload = { "YatraRouteId": int(route_id), "YatraId": int(yatra_id), "YatraBusId": int(bus_id) }
            # response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
            response = requests.post(api_url,json=payload)
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
        # route_list_api_url = "https://www.lakshyapratishthan.com/apis/listrouteall"
        route_list_api_url = f"{API_BASE_URL}listrouteall/"
        # response = requests.get(route_list_api_url, headers=headers, verify=False, timeout=10)
        response = requests.get(route_list_api_url)
        if response.status_code == 200:
            all_routes = response.json().get("message_data", [])
            routes = [route for route in all_routes if route.get("YatraRouteId") != "0"]
    except Exception as e:
        messages.error(request, f"Could not fetch routes: {e}")

    # Fetch all areas for the second filter
    try:
        # area_list_api_url = "https://www.lakshyapratishthan.com/apis/listarea"
        area_list_api_url = f"{API_BASE_URL}listarea/"
        # response = requests.get(area_list_api_url, headers=headers, verify=False, timeout=10)
        response = requests.get(area_list_api_url)
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
            # api_url = "https://www.lakshyapratishthan.com/apis/yatrabookings"
            api_url = f"{API_BASE_URL}yatrabookings/"
            payload = {"YatraRouteId": int(route_id)}
            # response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
            response = requests.post(api_url,json=payload)
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
            # route_list_api_url = "https://www.lakshyapratishthan.com/apis/listrouteall"
            route_list_api_url = f"{API_BASE_URL}listrouteall/"
            # route_response = requests.get(route_list_api_url, headers=headers, verify=False, timeout=10)
            route_response = requests.get(route_list_api_url)
            if route_response.status_code == 200:
                for route in route_response.json().get("message_data", []):
                    if str(route.get("YatraRouteId")) == str(route_id):
                        route_name = route.get("YatraRouteName")
                        break
        except Exception:
            pass # Continue even if this fails

        # Fetch all passenger data for the route
        # api_url = "https://www.lakshyapratishthan.com/apis/yatrabookings"
        api_url = f"{API_BASE_URL}yatrabookings/"
        payload = {"YatraRouteId": route_id}
        # response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
        response = requests.post(api_url,json=payload)
        
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




# ########### Diwali Kirana ####################


def home(request):
    """
    Renders the new home page after login.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    user_details = {
        "first_name": request.session.get("first_name", ""),
        "last_name": request.session.get("last_name", ""),
    }
    
    return render(request, "home.html", {"user": user_details})


def diwali_yatra_page(request):
    """
    Renders the placeholder page for Diwali Yatra.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')
    
    return render(request, "Diwali/diwali_yatra.html")



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# In views.py

# @csrf_exempt
# def diwali_registration(request):
#     """
#     API proxy for Diwali Kirana registration. Handles:
#     - action 'check_ration': Checks if a ration card exists.
#     - action 'submit': Creates OR Updates the head and family members.
#     """
#     if request.method != "POST":
#         return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

#     try:
#         # return JsonResponse({ 
#         #         "status": "success", 
#         #         "message": f"Registration process completed.and token is 101",
#         #         "TokenNo":101,
#         #         "reg_id":620,  
#         #     })
#         if request.POST.get("action") == "submit":
#             api_url = "http://127.0.0.1:8000/LakshyaPratishthan/api/diwaliregistration/"

#             # --- File Upload Logic (no changes here) ---
#             ration_card_url = None
#             ration_card_file = request.FILES.get("RationCardPhoto")
#             if ration_card_file:
#                 ext = os.path.splitext(ration_card_file.name)[1].lower() or '.jpg'
#                 file_name = f"ration-{uuid.uuid4().hex}{ext}"
#                 img_directory = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "ration_cards")
#                 os.makedirs(img_directory, exist_ok=True)
#                 save_path = os.path.join(img_directory, file_name)
#                 with open(save_path, "wb+") as dest:
#                     for chunk in ration_card_file.chunks():
#                         dest.write(chunk)
#                 ration_card_url = f"https://www.lakshyapratishthan.com/Yatra_darshan/static/assets/ration_cards/{file_name}"

#             head_details = json.loads(request.POST.get("head"))
#             family_members_data = json.loads(request.POST.get("family"))
#             ration_card_no = request.POST.get("rationCardNo")
#             record_id = request.POST.get("recordId")
#             TokenNo= head_details.get("tokenNo") or None
#             print(TokenNo,'2118')

#             # Convert date for head of family
#             dob_str_head = head_details.get("DateOfBirth", "")
#             if dob_str_head and '-' in dob_str_head:
#                 try: dob_str_head = datetime.strptime(dob_str_head, "%Y-%m-%d").strftime("%d/%m/%Y")
#                 except Exception: pass
            
#             head_payload = {
#                 "userMobileNo": head_details.get("userMobileNo"),
#                 "userAlternateMobileNo": head_details.get("userAlternateMobileNo", ""),
#                 "userFirstname": head_details.get("userFirstname"),
#                 "userMiddlename": head_details.get("userMiddlename", ""),
#                 "userLastname": head_details.get("userLastname"),
#                 "Gender": int(head_details.get("Gender", 1)),
#                 "DateOfBirth": dob_str_head,
#                 "RationCardNo": ration_card_no,
#                 "ParentId": "1",
#                 "AreaId": int(head_details.get("AreaId", 1)),
#                 "Address": head_details.get("address", ""),
#                 "RationCardPhoto": ration_card_url or head_details.get("existingRationCardPhoto", ""),
#                 "UserId":request.session["user_id"],
#                 # "UserId": 1,
#             }

#             if record_id and record_id != "0":
#                 head_payload["RegistrationId"] = int(record_id)
            
#             # --- IMPROVED DEBUGGING ---
#             print("--- SENDING HEAD DATA TO API ---")
#             print(json.dumps(head_payload, indent=2))
            
#             head_response = requests.post(api_url, json=head_payload, headers=headers, verify=False, timeout=10)
            
#             # --- IMPROVED DEBUGGING ---
#             print("--- RECEIVED HEAD RESPONSE FROM API ---")
#             print(f"Status Code: {head_response.status_code}")
#             print(f"Response Body: {head_response.text}")

#             if not head_response.ok: 
#                 return JsonResponse({"status": "error", "message": f"API Error ({head_response.status_code}) for head.", "details": head_response.text})
            
#             head_data = head_response.json()
#             if head_data.get("message_code") != 1000: 
#                 return JsonResponse({"status": "error", "message": f"Head registration failed: {head_data.get('message_text')}"})
            
#             head_reg_id = record_id if (record_id and record_id != "0") else head_data.get("message_data", {}).get("RegistrationId")
#             if not head_reg_id: 
#                 return JsonResponse({"status": "error", "message": "Could not get Head RegistrationId."})

#             family_members = [m for m in family_members_data if m.get("userFirstname", "").strip()]
#             member_results = []
#             for member in family_members:
#                 # ✅ --- CRITICAL FIX: Convert date format for family members ---
#                 dob_str_member = member.get("DateOfBirth", "")
#                 if dob_str_member and '-' in dob_str_member:
#                     try: dob_str_member = datetime.strptime(dob_str_member, "%Y-%m-%d").strftime("%d/%m/%Y")
#                     except Exception: pass
#                 # --- End of Fix ---

#                 member_payload = {
#                     "userMobileNo": head_details.get("userMobileNo"),
#                     "userAlternateMobileNo": head_details.get("userAlternateMobileNo",""),
#                     "userFirstname": member.get("userFirstname"),
#                     "userMiddlename": member.get("userMiddlename", ""),
#                     "userLastname": member.get("userLastname"),
#                     "Gender": int(member.get("Gender", 1)),
#                     "DateOfBirth": dob_str_member, # Uses the corrected date string
#                     "RationCardNo": ration_card_no,
#                     "ParentId": str(head_reg_id),
#                     "AreaId": int(head_details.get("AreaId", 1)),
#                     "Address": head_details.get("address", ""),
#                     "UserId":int(request.session["user_id"]),
#                 }
                
#                 member_id = member.get("registrationId")
#                 if member_id and member_id != "0":
#                     member_payload["RegistrationId"] = int(member_id)

#                 # --- IMPROVED DEBUGGING ---
#                 print(f"--- SENDING MEMBER DATA TO API: {member.get('userFirstname')} ---")
#                 print(json.dumps(member_payload, indent=2))

#                 member_resp = requests.post(api_url, json=member_payload, headers=headers, verify=False, timeout=10)
#                 print(member_resp.text,'2126----------')
                
#                 # --- IMPROVED DEBUGGING ---
#                 print(f"--- RECEIVED MEMBER RESPONSE FROM API: {member.get('userFirstname')} ---")
#                 print(f"Status Code: {member_resp.status_code}")
#                 print(f"Response Body: {member_resp.text}")

#                 member_results.append({ "name": f"{member.get('userFirstname')} {member.get('userLastname')}".strip(), "success": member_resp.ok and member_resp.json().get("message_code") == 1000, "response": member_resp.json() if member_resp.ok else {"text": member_resp.text} })

#             # --- Token Generation Logic (no changes here) ---
#             qr_dir = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "img", "tokenqr")
#             os.makedirs(qr_dir, exist_ok=True)
#             qr_filename = f"{head_reg_id}.png"
#             qr_path = os.path.join(qr_dir, qr_filename)
#             if not os.path.exists(qr_path):
#                 token_resp = requests.post(" ", json={"RegistrationId":head_reg_id,"RationCardNo":ration_card_no,"TokenNo":TokenNo}, headers=headers, verify=False, timeout=10)
#                 if token_resp.ok and token_resp.json().get('message_data'):
#                     TokenURL = token_resp.json().get('message_data').get('TokenURL') or None
#                     TokenNo1 = token_resp.json().get('message_data').get('TokenNo') or None
#                     if TokenURL:
#                         qr_img = qrcode.make(TokenURL)
#                         qr_img.save(qr_path)

#             else:
#                 TokenNo1=0
#                 print('already token genearation...')
#             # Return a more detailed success response
#             return JsonResponse({ 
#                 "status": "success", 
#                 "message": f"Registration process completed.and token is {TokenNo}",
#                 "TokenNo":TokenNo if TokenNo else TokenNo1,
#                 "reg_id":head_reg_id, 
#                 "head_registration": head_data, 
#                 "member_registrations": member_results 
#             })
        
#         # This is for the initial check, it is correct
#         elif request.method == "POST":
#             data = json.loads(request.body.decode("utf-8"))
#             if data.get("action") == "check_ration":
#                 ration_card_no = data.get("RationCardNo")
#                 if not ration_card_no: return JsonResponse({"message_code": 999, "message_text": "Ration Card number is required."})
#                 api_url_check = "http://127.0.0.1:8000/LakshyaPratishthan/api/check_rationcard/"
#                 payload = {"SearchString": ration_card_no}
#                 response = requests.post(api_url_check, json=payload, headers=headers, verify=False, timeout=10)
#                 return JsonResponse(response.json())

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return JsonResponse({"status": "error", "message": f"An unexpected error occurred: {str(e)}"}, status=500)

#     return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)






@csrf_exempt
def diwali_registration(request):
    """
    API proxy for Diwali Kirana registration. Handles:
    - action 'check_ration': Checks if a ration card exists.
    - action 'submit': Creates OR Updates the head and family members.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

    try:
        # return JsonResponse({ 
        #         "status": "success", 
        #         "message": f"Registration process completed.and token is 101",
        #         "TokenNo":101,
        #         "reg_id":620,  
        #     })
        if request.POST.get("action") == "submit":
            api_url = "http://127.0.0.1:8000/LakshyaPratishthan/api/diwaliregistration/"

            # --- File Upload Logic (no changes here) ---
            ration_card_url = None
            ration_card_file = request.FILES.get("RationCardPhoto")
            if ration_card_file:
                ext = os.path.splitext(ration_card_file.name)[1].lower() or '.jpg'
                file_name = f"ration-{uuid.uuid4().hex}{ext}"
                img_directory = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "ration_cards")
                os.makedirs(img_directory, exist_ok=True)
                save_path = os.path.join(img_directory, file_name)
                with open(save_path, "wb+") as dest:
                    for chunk in ration_card_file.chunks():
                        dest.write(chunk)
                ration_card_url = f"https://www.lakshyapratishthan.com/Yatra_darshan/static/assets/ration_cards/{file_name}"

            voter_id_url = None
            voter_id_file = request.FILES.get("VoterIdPhoto")
            if voter_id_file:
                ext = os.path.splitext(voter_id_file.name)[1].lower() or '.jpg'
                file_name = f"voter-{uuid.uuid4().hex}{ext}"
                # Save to a new directory to keep things organized
                img_directory = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "voter_ids")
                os.makedirs(img_directory, exist_ok=True)
                save_path = os.path.join(img_directory, file_name)
                with open(save_path, "wb+") as dest:
                    for chunk in voter_id_file.chunks():
                        dest.write(chunk)
                # This should be the public URL to access the file
                voter_id_url = f"/static/assets/voter_ids/{file_name}"

            head_details = json.loads(request.POST.get("head"))
            family_members_data = json.loads(request.POST.get("family"))
            ration_card_no = request.POST.get("rationCardNo")
            record_id = request.POST.get("recordId")
            TokenNo= head_details.get("tokenNo") or None
            print(TokenNo,'2118')

            # Convert date for head of family
            dob_str_head = head_details.get("DateOfBirth", "")
            if dob_str_head and '-' in dob_str_head:
                try: dob_str_head = datetime.strptime(dob_str_head, "%Y-%m-%d").strftime("%d/%m/%Y")
                except Exception: pass
            
            head_payload = {
                "userMobileNo": head_details.get("userMobileNo"),
                "userAlternateMobileNo": head_details.get("userAlternateMobileNo", ""),
                "userFirstname": head_details.get("userFirstname"),
                "userMiddlename": head_details.get("userMiddlename", ""),
                "userLastname": head_details.get("userLastname"),
                "Gender": int(head_details.get("Gender", 1)),
                "DateOfBirth": dob_str_head,
                "RationCardNo": ration_card_no,
                "ParentId": "1",
                "AreaId": int(head_details.get("AreaId", 1)),
                "Address": head_details.get("address", ""),
                "RationCardPhoto": ration_card_url or head_details.get("existingRationCardPhoto", ""),
                "UserId":request.session["user_id"],
                "VoterIdProof": voter_id_url or head_details.get("existingVoterIdPhoto", ""),
                "Age": head_details.get("Age", 0),
            }

            if record_id and record_id != "0":
                head_payload["RegistrationId"] = int(record_id)
            
            # --- IMPROVED DEBUGGING ---
            print("--- SENDING HEAD DATA TO API ---")
            print(json.dumps(head_payload, indent=2))
            
            head_response = requests.post(api_url, json=head_payload, headers=headers, verify=False, timeout=10)
            
            # --- IMPROVED DEBUGGING ---
            print("--- RECEIVED HEAD RESPONSE FROM API ---")
            print(f"Status Code: {head_response.status_code}")
            print(f"Response Body: {head_response.text}")

            if not head_response.ok: 
                return JsonResponse({"status": "error", "message": f"API Error ({head_response.status_code}) for head.", "details": head_response.text})
            
            head_data = head_response.json()
            if head_data.get("message_code") != 1000: 
                return JsonResponse({"status": "error", "message": f"Head registration failed: {head_data.get('message_text')}"})
            
            head_reg_id = record_id if (record_id and record_id != "0") else head_data.get("message_data", {}).get("RegistrationId")
            if not head_reg_id: 
                return JsonResponse({"status": "error", "message": "Could not get Head RegistrationId."})

            family_members = [m for m in family_members_data if m.get("userFirstname", "").strip()]
            member_results = []
            for member in family_members:
                # ✅ --- CRITICAL FIX: Convert date format for family members ---
                dob_str_member = member.get("DateOfBirth", "")
                if dob_str_member and '-' in dob_str_member:
                    try: dob_str_member = datetime.strptime(dob_str_member, "%Y-%m-%d").strftime("%d/%m/%Y")
                    except Exception: pass
                # --- End of Fix ---

                member_payload = {
                    "userMobileNo": head_details.get("userMobileNo"),
                    "userAlternateMobileNo": head_details.get("userAlternateMobileNo",""),
                    "userFirstname": member.get("userFirstname"),
                    "userMiddlename": member.get("userMiddlename", ""),
                    "userLastname": member.get("userLastname"),
                    "Gender": int(member.get("Gender", 1)),
                    "DateOfBirth": dob_str_member, # Uses the corrected date string
                    "RationCardNo": ration_card_no,
                    "ParentId": str(head_reg_id),
                    "AreaId": int(head_details.get("AreaId", 1)),
                    "Address": head_details.get("address", ""),
                    "UserId":request.session["user_id"],
                }
                
                member_id = member.get("registrationId")
                if member_id and member_id != "0":
                    member_payload["RegistrationId"] = int(member_id)

                # --- IMPROVED DEBUGGING ---
                print(f"--- SENDING MEMBER DATA TO API: {member.get('userFirstname')} ---")
                print(json.dumps(member_payload, indent=2))

                member_resp = requests.post(api_url, json=member_payload, headers=headers, verify=False, timeout=10)
                
                # --- IMPROVED DEBUGGING ---
                print(f"--- RECEIVED MEMBER RESPONSE FROM API: {member.get('userFirstname')} ---")
                print(f"Status Code: {member_resp.status_code}")
                print(f"Response Body: {member_resp.text}")

                member_results.append({ "name": f"{member.get('userFirstname')} {member.get('userLastname')}".strip(), "success": member_resp.ok and member_resp.json().get("message_code") == 1000, "response": member_resp.json() if member_resp.ok else {"text": member_resp.text} })

            # --- Token Generation Logic () ---
            qr_dir = os.path.join(settings.BASE_DIR, "staticfiles", "assets", "img", "tokenqr")
            os.makedirs(qr_dir, exist_ok=True)
            qr_filename = f"{head_reg_id}.png"
            qr_path = os.path.join(qr_dir, qr_filename)
            if not os.path.exists(qr_path):
                token_resp = requests.post("http://127.0.0.1:8000/LakshyaPratishthan/api/add_diwali_kirana/", json={"RegistrationId":head_reg_id,"RationCardNo":ration_card_no,"TokenNo":TokenNo}, headers=headers, verify=False, timeout=10)
                print(token_resp.text,'2364')
                if token_resp.ok and token_resp.json().get('message_data'):
                    TokenURL = token_resp.json().get('message_data').get('TokenURL') or None
                    TokenNo1 = token_resp.json().get('message_data').get('TokenNo') or None
                    if TokenURL:
                        qr_img = qrcode.make(TokenURL)
                        qr_img.save(qr_path)

            else:
                TokenNo1=0
                print('already token genearation...')
            # Return a more detailed success response
            return JsonResponse({ 
                "status": "success", 
                "message": f"Registration process completed.and token is {TokenNo}",
                "TokenNo":TokenNo if TokenNo else TokenNo1,
                "reg_id":head_reg_id, 
                "head_registration": head_data, 
                "member_registrations": member_results 
            })
        
        # This is for the initial check, it is correct
        elif request.method == "POST":
            data = json.loads(request.body.decode("utf-8"))
            if data.get("action") == "check_ration":
                ration_card_no = data.get("RationCardNo")
                if not ration_card_no: return JsonResponse({"message_code": 999, "message_text": "Ration Card number is required."})
                api_url_check = "http://127.0.0.1:8000/LakshyaPratishthan/api/check_rationcard/"
                payload = {"SearchString": ration_card_no}
                response = requests.post(api_url_check, json=payload, headers=headers, verify=False, timeout=10)
                return JsonResponse(response.json())

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"status": "error", "message": f"An unexpected error occurred: {str(e)}"}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)




def diwali_all_registrations(request):
    """
    Fetches all Diwali Kirana registrations using the dedicated 'listdiwalikirana' API
    and renders them in a list.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    all_families = []
    try:
        api_url = "http://127.0.0.1:8000/LakshyaPratishthan/api/list_diwalikirana/"

        payload = {} 
        
        print(f"Calling API to list all registrations: {api_url}")

        response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=20)
        
        print(f"API Response Status Code: {response.status_code}")
        try:
            response_data = response.json()
            print(f"API Response JSON: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"API Response Text: {response.text}")
            response_data = None

        if response.status_code == 200 and response_data:
            if response_data.get("message_code") == 1000 and isinstance(response_data.get("message_data"), list):
                all_records = response_data.get("message_data")
                
                families_dict = {}
                for record in all_records:
                    ration_card = record.get("RationCardNo")
                    if ration_card:
                        if ration_card not in families_dict:
                            families_dict[ration_card] = []
                        families_dict[ration_card].append(record)
                
                for ration_card, members in families_dict.items():
                    members.sort(key=lambda x: int(x.get("RegistrationId", 0)))
                    head = next((m for m in members if m.get("ParentId") in ["1", str(m.get("RegistrationId"))]), members[0])
                    # token_res = requests.post("https://www.lakshyapratishthan.com/apis/diwalikirana", json={"RegistrationId":head.get("RegistrationId"),"RationCardNo":ration_card},  headers=headers, verify=False, timeout=20)
                    # print(token_res.text)
                    token_no = head.get("TokenNo") or "N/A"
            
                    family_data = {
                        'head': head,
                        'members': [m for m in members if str(m.get("RegistrationId")) != str(head.get("RegistrationId"))],
                        'ration_card_no': ration_card,
                        'token': token_no or "N/A",
                        'ration_card_photo': head.get("RationCardPhoto") 
                    }
                    all_families.append(family_data)

                all_families.sort(key=lambda x: int(x['token']) if str(x['token']).isdigit() else 0)


            else:
                messages.error(request, f"API returned an error: {response_data.get('message_text', 'No message')}")
        else:
            messages.error(request, f"API request failed with status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Could not connect to the API: {str(e)}")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")

    print(all_families)
    return render(request, "Diwali/diwali_all_registrations.html", {"families": all_families})




from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
# ... (imports and other views are unchanged) ...

# The headers variable should be available here
headers = {"Content-Type": "application/json"}
# ... (imports and other views are unchanged) ...

# The headers variable should be available here
headers = {"Content-Type": "application/json"}

# ... (imports and other views are unchanged) ...

headers = {"Content-Type": "application/json"}

@csrf_exempt
def rationcardscan(request):
    """
    Handles both displaying the token entry form and showing family details.
    - GET: Fetches family details and status.
    - POST: Updates the delivery status using the Token Number.
    """
    # --- POST request logic is now CORRECTED ---
    if request.method == 'POST':
        try:
            token_no = request.POST.get('token')
            status = request.POST.get('status')
            
            if not token_no or not status:
                return JsonResponse({"status": "error", "message": "Token and status are required."}, status=400)

            api_url = "http://127.0.0.1:8000/LakshyaPratishthan/api/update_token_status/"
            
            # ✅ --- CRITICAL FIX: Changed "TokenQR" to "TokenNo" and ensure it's an integer ---
            payload = {
                "TokenNo": int(token_no),
                "Status": int(status)
            }
            
            response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
            
            if response.ok and response.json().get("message_code") == 1000:
                return JsonResponse({"status": "success", "message": "Status updated successfully."})
            else:
                error_message = response.json().get("message_text", "Failed to update status.")
                return JsonResponse({"status": "error", "message": error_message}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    # --- GET request logic remains unchanged and is correct ---
    token = request.GET.get('t') or None
    context = {
        "token": token,
        "head": None,
        "members": [],
        "error": None,
        "delivery_status": 0
    }

    if token:
        try:
            token_number = int(token)
            api_url = "http://127.0.0.1:8000/LakshyaPratishthan/api/list_family/"
            payload = {"TokenNo": token_number}
            response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

            if response.ok:
                data = response.json()
                if data.get("message_code") == 1000 and isinstance(data.get("message_data"), list):
                    all_members = data["message_data"]
                    if not all_members:
                        context["error"] = "No family found for this token."
                    else:
                        head = next((p for p in all_members if p.get("ParentId") == "1" or p.get("ParentId") == p.get("RegistrationId")), all_members[0])
                        context["head"] = head
                        context["members"] = [p for p in all_members if p.get("RegistrationId") != head.get("RegistrationId")]
                        
                        found_status = "0"
                        for member in all_members:
                            status_val = member.get("Status")
                            if status_val in ["1", "2"]:
                                found_status = status_val
                                break
                        context["delivery_status"] = int(found_status)
                else:
                    context["error"] = data.get("message_text", "Could not process the request.")
            else:
                context["error"] = f"API request failed with status code {response.status_code}."
        except (ValueError, TypeError):
            context["error"] = "Invalid Token Format. Please enter numbers only."
        except Exception as e:
            context["error"] = f"An unexpected error occurred: {str(e)}"

    return render(request, 'Diwali/ration_card_scan.html', context)



def change_diwali_token(request):
    """
    API proxy to change a Diwali Kirana token number.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        old_token = data.get("OldTokenNo")
        new_token = data.get("NewTokenNo")
        reg_id = data.get("RegistrationId")
        print(old_token)

        if not all([old_token, new_token, reg_id]):
            return JsonResponse({"status": "error", "message": "Missing required data."}, status=400)

        api_url = "http://127.0.0.1:8000/LakshyaPratishthan/api/change_diwali_token/"
        payload = {
            "OldTokenNo": int(old_token),
            "NewTokenNo": int(new_token),
            "RegistrationId": int(reg_id)
        }
        
        # Note: 'headers' should be defined globally or passed in. Assuming it's defined elsewhere in your file.
        response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

        if not response.ok:
            return JsonResponse({"status": "error", "message": f"API server error: {response.status_code}"}, status=502)

        api_data = response.json()
        if api_data.get("message_code") == 1000:
            return JsonResponse({"status": "success", "message": api_data.get("message_text", "Token changed successfully.")})
        else:
            return JsonResponse({"status": "error", "message": api_data.get("message_text", "Failed to change token.")})

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"An unexpected error occurred: {str(e)}"}, status=500)
    

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
def diwali_report_page(request):
    """
    Directly generates and serves an Excel file with all registration data.
    This view does not render an HTML page.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    all_families = []
    
    try:
        # --- This logic remains the same: it fetches and prepares the data ---
        area_map = {}
        area_api_url = "http://127.0.0.1:8000/LakshyaPratishthan/api/listareaall/"
        area_response = requests.post(area_api_url, json={}, headers=headers, verify=False, timeout=15)
        if area_response.ok:
            area_data = area_response.json()
            if area_data.get("message_code") == 1000:
                for area in area_data["message_data"]:
                    area_map[area.get("AreaId")] = area.get("AreaName")

        registrations_api_url = "http://127.0.0.1:8000/LakshyaPratishthan/api/list_diwalikirana/"
        reg_response = requests.post(registrations_api_url, json={}, headers=headers, verify=False, timeout=30)
        
        if reg_response.ok:
            response_data = reg_response.json()
            if response_data.get("message_code") == 1000:
                all_records = response_data["message_data"]
                families_dict = {}
                for record in all_records:
                    ration_card = record.get("RationCardNo", "").strip()
                    if ration_card:
                        families_dict.setdefault(ration_card, []).append(record)
                
                for ration_card, members in families_dict.items():
                    head = next((m for m in members if m.get("ParentId") in ["1", str(m.get("RegistrationId"))]), members[0])
                    head['AreaName'] = area_map.get(head.get("AreaId"), "Unknown Area")
                    all_families.append({'head': head})
        
        # --- EXCEL GENERATION LOGIC IS NOW THE MAIN PART OF THE VIEW ---
        wb = Workbook()
        ws = wb.active
        ws.title = "Diwali Registrations"
        
        # Define headers
        headers_list = ["Token No", "Full Name", "Mobile No", "Alternate Mobile", "Address", "Area", "Ration Card No"]
        ws.append(headers_list)

        # Style the header row
        for cell in ws["1:1"]:
            cell.font = Font(bold=True)
        
        # Add data rows
        for family in all_families:
            head = family['head']
            full_name = f"{head.get('Firstname', '')} {head.get('Middlename', '')} {head.get('Lastname', '')}".strip()
            row_data = [
                head.get('TokenNo', 'N/A'),
                full_name,
                head.get('MobileNo', ''),
                head.get('AlternateMobileNo', ''),
                head.get('Address', ''),
                head.get('AreaName', ''),
                head.get('RationCardNo', '') # Added Ration Card Number
            ]
            ws.append(row_data)

        # Create the response to serve the file
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="diwali_registrations.xlsx"'
        wb.save(response)
        return response

    except Exception as e:
        messages.error(request, f"An error occurred while generating the report: {str(e)}")
        # Redirect back to the home page or another safe page on error
        return redirect('home')    
    


def manage_family_members(request, ration_card_no):
    """
    Fetches data for a single family by ration card number and renders the 
    member management page.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    head_details = None
    family_members = []
    
    try:
        # We reuse the existing API to get all members for this ration card
        api_url_check = "http://127.0.0.1:8000/LakshyaPratishthan/api/check_rationcard/"
        payload = {"SearchString": ration_card_no}
        response = requests.post(api_url_check, json=payload, headers=headers, verify=False, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("message_code") == 1000 and data.get("message_data"):
                all_records = data["message_data"]
                # Find the head of the family
                head_details = next((m for m in all_records if m.get("ParentId") in ["1", str(m.get("RegistrationId"))]), all_records[0])
                # List everyone else as a family member
                family_members = [m for m in all_records if str(m.get("RegistrationId")) != str(head_details.get("RegistrationId"))]
            else:
                messages.error(request, f"Could not find family with ration card: {ration_card_no}")
        else:
            messages.error(request, "Failed to connect to the data API.")

    except requests.exceptions.RequestException as e:
        messages.error(request, f"API connection error: {e}")
        
    context = {
        'head': head_details,
        'members': family_members,
        'ration_card_no': ration_card_no
    }
    return render(request, "Diwali/manage_family_members.html", context)


@csrf_exempt
def delete_diwali_member(request, reg_id):
    """
    API proxy to delete a registration record.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid method"}, status=405)

    try:
        # This will call the new API endpoint we will create in Step 5
        api_url = f"http://127.0.0.1:8000/LakshyaPratishthan/api/delete_diwali_member/{reg_id}/"
        response = requests.post(api_url, headers=headers, verify=False, timeout=10)
        
        if response.ok:
            return JsonResponse(response.json())
        else:
            return JsonResponse({"status": "error", "message": "API call failed"}, status=response.status_code)
            
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)





# your_app/views.py

def darshan_yatra_management(request):
    """
    Fetches all families and all areas to display on the Darshan Yatra page,
    which is focused on adding members to existing families.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    all_families = []
    all_areas = []
    area_map = {} # Dictionary to map AreaId to AreaName

    try:
        # 1. Fetch all ACTIVE areas using your 'listarea' API
        # ✅ CHANGED: Updated the API endpoint URL
        area_api_url = "http://127.0.0.1:8000/LakshyaPratishthan/api/listarea/"
        
        # ✅ CHANGED: Switched from POST to GET request as required by your API decorator @api_view(['GET'])
        area_response = requests.get(area_api_url, headers=headers, verify=False, timeout=15)
        
        if area_response.ok and area_response.json().get("message_code") == 1000:
            all_areas = area_response.json().get("message_data", [])
            # Create the mapping (this logic remains the same)
            for area in all_areas:
                area_map[area.get("AreaId")] = area.get("AreaName")

        # 2. Fetch all registered families (this logic is unchanged)
        api_url = "http://127.0.0.1:8000/LakshyaPratishthan/api/list_diwalikirana/"
        response = requests.post(api_url, json={}, headers=headers, verify=False, timeout=20)

        if response.ok and response.json().get("message_code") == 1000:
            all_records = response.json().get("message_data", [])
            
            families_dict = {}
            for record in all_records:
                ration_card = record.get("RationCardNo")
                if ration_card:
                    families_dict.setdefault(ration_card, []).append(record)
            
            for ration_card, members in families_dict.items():
                members.sort(key=lambda x: int(x.get("RegistrationId", 0)))
                head = next((m for m in members if m.get("ParentId") in ["1", str(m.get("RegistrationId"))]), members[0])
                
                # Add the AreaName to the head's data using the map
                head['AreaName'] = area_map.get(head.get("AreaId"), "Unknown Area")
                
                family_data = {
                    'head': head,
                    'members': [m for m in members if str(m.get("RegistrationId")) != str(head.get("RegistrationId"))],
                    'ration_card_no': ration_card,
                }
                all_families.append(family_data)
            
            all_families.sort(key=lambda x: x['head'].get('Firstname', '').lower())
        else:
            api_error_message = "Unknown API error"
            try:
                api_error_message = response.json().get('message_text', 'No message')
            except:
                pass 
            messages.error(request, f"API returned an error while fetching families: {api_error_message}")


    except requests.exceptions.RequestException as e:
        messages.error(request, f"Could not connect to the API: {str(e)}")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")

    context = {
        "families": all_families,
        "areas": all_areas
    }
    return render(request, "Diwali/darshan_yatra_management.html", context)




# Event Managment ###################

def event_list_page(request):
    """
    Fetches all non-deleted events from the API and displays them on a page.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login') 

    events = []
    try:
        api_url = f"{API_BASE_URL}event_list/" 
        # Make sure you are using HEADERS, not a variable 'headers'
        response = requests.get(api_url, headers=headers, verify=False, timeout=20)
        
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get("message_code") == 1000:
                # Get the raw list of event dictionaries from the API
                events_from_api = response_data.get("message_data", [])

                # --- START OF THE FIX ---
                # Process the list to convert date strings into datetime objects
                for event in events_from_api:
                    datetime_str = event.get('startDateTime')
                    if datetime_str:
                        try:
                            # Parse the string and replace it with a real datetime object
                            event['startDateTime'] = datetime.fromisoformat(datetime_str)
                        except (ValueError, TypeError):
                            # If the date string is bad or null, set it to None
                            event['startDateTime'] = None
                
                # Now, events is the processed list
                events = events_from_api
                # --- END OF THE FIX ---

            else:
                error_message = response_data.get('message_text', 'An unknown API error occurred.')
                messages.error(request, f"API Error: {error_message}")
        else:
            messages.error(request, f"API request failed with status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        messages.error(request, f"Could not connect to the API: {e}")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {e}")

    return render(request, "events/event_list.html", {"events": events})


# def add_edit_event_page(request, event_id=None):
#     """
#     Handles both creating a new event and editing an existing one.
#     """
#     if 'user_id' not in request.session:
#         messages.error(request, "Please login first.")
#         return redirect('login')

#     event_data = {}
    
#     if event_id:
#         try:
#             api_url = f"{API_BASE_URL}event_list/?eventId={event_id}" 
#             response = requests.get(api_url, headers=headers, verify=False, timeout=20)
#             if response.status_code == 200 and response.json().get("message_code") == 1000:
#                 event_data = response.json().get("message_data", [{}])[0]
#             else:
#                 messages.error(request, "Could not find the event to edit.")
#                 return redirect('event_list_page')
#         except Exception as e:
#             messages.error(request, f"Error fetching event details: {e}")
#             return redirect('event_list_page')

#     # Handle form submission
#     if request.method == 'POST':
#         payload = {
#             'title': request.POST.get('title'),
#             'description': request.POST.get('description'),
#             'eventType': request.POST.get('eventType'),
#             'capacity': request.POST.get('capacity'),
#             'entryFees': request.POST.get('entryFees'),
#             'startDateTime': request.POST.get('startDateTime') or None, 
#             'endDateTime': request.POST.get('endDateTime') or None,
#             'registrationStart': request.POST.get('registrationStart') or None,
#             'registrationEnd': request.POST.get('registrationEnd') or None,
#         }
        
#         payload_clean = {k: v for k, v in payload.items() if v is not None and v != ''}

#         try:
#             if event_id:
#                 payload_clean['eventId'] = event_id
#                 api_url = f"{API_BASE_URL}event_update/"
#                 response = requests.post(api_url, json=payload_clean, headers=headers, verify=False)
#                 action_text = "updated"
#             else:
#                 api_url = f"{API_BASE_URL}event_create/" 
#                 response = requests.post(api_url, json=payload_clean, headers=headers, verify=False)
#                 action_text = "created"
            
#             if response.status_code == 200:
#                 response_data = response.json()
#                 if response_data.get("message_code") == 1000:
#                     messages.success(request, f"Event {action_text} successfully!")
#                     return redirect('event_list_page')
#                 else:
#                     messages.error(request, f"Failed to {action_text} event: {response_data.get('message_text')}")
#             else:
#                 messages.error(request, f"API request failed with status {response.status_code}.")

#         except requests.exceptions.RequestException as e:
#             messages.error(request, f"Could not connect to the API: {e}")
            
#     return render(request, "events/event_form.html", {"event": event_data})


# Darshan Yatra views.py

import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime # <--- IMPORT THIS

# ... (keep your API_BASE_URL and HEADERS as they are) ...
# ... (event_list_page and delete_event_page are fine, no changes needed there) ...

def add_edit_event_page(request, event_id=None):
    """
    Handles both creating a new event and editing an existing one.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    event_data = {}
    
    # If editing, fetch the existing event data
    if event_id:
        try:
            api_url = f"{API_BASE_URL}event_list/?eventId={event_id}"
            response = requests.get(api_url, headers=headers, verify=False, timeout=20)
            if response.status_code == 200 and response.json().get("message_code") == 1000:
                event_data = response.json().get("message_data", [{}])[0]

                # --- START OF THE FIX ---
                # List of date fields to process
                date_fields = ['startDateTime', 'endDateTime', 'registrationStart', 'registrationEnd']
                
                for field in date_fields:
                    # Get the date string from the API data (e.g., "2025-11-01T23:30:00+05:30")
                    datetime_str = event_data.get(field)
                    
                    if datetime_str:
                        try:
                            # Parse the ISO format string into a datetime object
                            dt_obj = datetime.fromisoformat(datetime_str)
                            
                            # Format it into the string that <input type="datetime-local"> needs
                            # The required format is YYYY-MM-DDTHH:MM
                            event_data[field] = dt_obj.strftime('%Y-%m-%dT%H:%M')
                        except (ValueError, TypeError):
                            # If parsing fails or the field is not a string, leave it blank
                            event_data[field] = ""
                # --- END OF THE FIX ---

            else:
                messages.error(request, "Could not find the event to edit.")
                return redirect('event_list_page')
        except Exception as e:
            messages.error(request, f"Error fetching event details: {e}")
            return redirect('event_list_page')

    # ... (The rest of your POST handling logic is fine, no changes needed there) ...
    if request.method == 'POST':
        # Collect data from the form
        payload = {
            'title': request.POST.get('title'),
            'description': request.POST.get('description'),
            'eventType': request.POST.get('eventType'),
            'capacity': request.POST.get('capacity'),
            'entryFees': request.POST.get('entryFees'),
            'startDateTime': request.POST.get('startDateTime') or None,
            'endDateTime': request.POST.get('endDateTime') or None,
            'registrationStart': request.POST.get('registrationStart') or None,
            'registrationEnd': request.POST.get('registrationEnd') or None,
        }
        payload_clean = {k: v for k, v in payload.items() if v is not None and v != ''}

        try:
            if event_id:
                payload_clean['eventId'] = event_id
                api_url = f"{API_BASE_URL}event_update/"
                response = requests.post(api_url, json=payload_clean, headers=headers, verify=False)
                action_text = "updated"
            else:
                api_url = f"{API_BASE_URL}event_create/"
                response = requests.post(api_url, json=payload_clean, headers=headers, verify=False)
                action_text = "created"
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("message_code") == 1000:
                    messages.success(request, f"Event {action_text} successfully!")
                    return redirect('event_list_page')
                else:
                    messages.error(request, f"Failed to {action_text} event: {response_data.get('message_text')}")
            else:
                messages.error(request, f"API request failed with status {response.status_code}.")

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Could not connect to the API: {e}")
            
    return render(request, "events/event_form.html", {"event": event_data})

def delete_event_page(request, event_id):
    """
    Handles the deletion of an event by calling the delete API.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')
        
    if request.method == 'POST':
        try:
            api_url = f"{API_BASE_URL}event_delete/" 
            payload = {'eventId': event_id}
            response = requests.post(api_url, json=payload, headers=headers, verify=False)
            
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("message_code") == 1000:
                    messages.success(request, "Event deleted successfully.")
                else:
                    messages.error(request, f"Failed to delete event: {response_data.get('message_text')}")
            else:
                 messages.error(request, f"API request failed with status {response.status_code}.")

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Could not connect to the API: {e}")

    return redirect('event_list_page')




# def configure_event_fields_page(request, event_id):
#     """
#     Handles fetching and updating the registration field configuration for an event
#     by calling our custom API.
#     """
#     if 'user_id' not in request.session:
#         messages.error(request, "Please login first.")
#         return redirect('login')

#     context = {
#         "event_id": event_id,
#         "config_data": {} # Initialize empty config data
#     }
#     api_url = f"{API_BASE_URL}events/{event_id}/configure-fields/"

#     # --- GET Request Logic: Fetch existing configuration to display ---
#     try:
#         response = requests.get(api_url, headers=headers, verify=False, timeout=20)
        
#         if response.status_code == 200:
#             context["config_data"] = response.json()
#         elif response.status_code == 404:
#              messages.warning(request, "This event has not been configured yet. Select fields and save.")
#              # We still need all possible fields to render the form
#              # Let's create a default structure if the API returns 404
#              context["config_data"] = {
#                  "event_title": "Unknown Event", # You might want to fetch event title separately
#                  "all_possible_fields": [
#                     'firstname', 'middlename', 'lastname', 'mobileNo', 'alternateMobileNo',
#                     'BookingMobileNo', 'aadharNumber', 'bloodGroup', 'dateOfBirth',
#                     'zonePreference', 'gender', 'areaId', 'address', 'photoFileName',
#                     'idProofFileName', 'voterIdProof', 'age', 'ration_card_no', 'ration_card_photo'
#                  ],
#                  "selected_fields": []
#              }
#         else:
#             messages.error(request, f"Could not fetch configuration. API returned status {response.status_code}.")
#             return redirect('event_list_page') # Redirect to your event list page
            
#     except requests.exceptions.RequestException as e:
#         messages.error(request, f"Error connecting to the API: {e}")
#         return redirect('event_list_page')

#     # --- POST Request Logic: Handle form submission ---
#     if request.method == 'POST':
#         # Getlist is used to capture all values from checkboxes with the same name
#         selected_fields = request.POST.getlist('selected_fields')
        
#         payload = {
#             'selected_fields': selected_fields
#         }

#         try:
#             # The API uses POST for updates as per our design
#             response = requests.post(api_url, json=payload, headers=headers, verify=False)
            
#             if response.status_code == 200:
#                 response_data = response.json()
#                 messages.success(request, response_data.get('message', 'Configuration updated successfully!'))
#                 return redirect('event_list_page') # Redirect on success
#             else:
#                 messages.error(request, f"API request failed with status {response.status_code}.")

#         except requests.exceptions.RequestException as e:
#             messages.error(request, f"Could not connect to the API to save changes: {e}")

#     # Render the page on a GET request or if a POST request fails
#     return render(request, "events/configure_fields_form.html", context)



def configure_event_fields_page(request, event_id):
    """
    Handles fetching and updating the registration field configuration for an event.
    This version has the CORRECT API URL and works with your standardized backend.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    context = {
        "event_id": event_id,
        "config_data": {}
    }
    
    # FIX: The URL now correctly matches your backend urls.py
    api_url = f"{API_BASE_URL}event_configure/{event_id}/"

    # --- GET Request Logic ---
    if request.method == 'GET':
        try:
            response = requests.get(api_url, headers=headers, verify=False, timeout=20)
            
            if response.status_code == 200:
                api_data = response.json()
                
                if api_data.get('message_code') == 1000:
                    if api_data.get('message_data'):
                        context['config_data'] = api_data['message_data'][0]
                        if not context['config_data'].get('selected_fields'):
                            messages.warning(request, "This event has not been configured yet. Select fields and save.")
                    else:
                        messages.error(request, "API returned success but the data was empty.")
                        return redirect('event_list_page')
                else:
                    error_text = api_data.get('message_text', 'An unknown API error occurred.')
                    messages.error(request, error_text)
                    return redirect('event_list_page')
            else:
                messages.error(request, f"API server error. Status: {response.status_code}")
                return redirect('event_list_page')
                
        except requests.exceptions.RequestException as e:
            messages.error(request, f"Error connecting to the API: {e}")
            return redirect('event_list_page')

    # --- POST Request Logic ---
    if request.method == 'POST':
        selected_fields = request.POST.getlist('selected_fields')
        payload = {'selected_fields': selected_fields}

        try:
            response = requests.post(api_url, json=payload, headers=headers, verify=False)
            
            if response.status_code == 200:
                api_data = response.json()
                if api_data.get('message_code') == 1000:
                    messages.success(request, 'Configuration updated successfully!')
                    return redirect('event_list_page')
                else:
                    error_text = api_data.get('message_text', 'Failed to save configuration.')
                    messages.error(request, error_text)
                    # Re-fetch data to show the form again with the error message
                    get_response = requests.get(api_url, headers=headers, verify=False)
                    if get_response.status_code == 200 and get_response.json().get('message_code') == 1000:
                         context['config_data'] = get_response.json()['message_data'][0]
            else:
                messages.error(request, f"API server error on save. Status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            messages.error(request, f"Could not connect to the API to save changes: {e}")

    return render(request, "events/configure_fields_form.html", context)


def view_registrations_page(request, event_id):
    """
    Displays a dynamic table of registrations for a specific event.
    """
    if 'user_id' not in request.session:
        messages.error(request, "Please login first.")
        return redirect('login')

    context = {
        'registration_data': {},
        'event_id': event_id
    }
    # Use the new API URL
    api_url = f"{API_BASE_URL}event_registrations/{event_id}/"

    try:
        response = requests.get(api_url, headers=headers, verify=False, timeout=20)
        
        if response.status_code == 200:
            api_data = response.json()
            if api_data.get('message_code') == 1000:
                if api_data.get('message_data'):
                    context['registration_data'] = api_data['message_data'][0]
                else:
                    # This handles the case where no fields are configured
                    messages.warning(request, api_data.get('message_text', 'No fields configured for this event.'))
                    context['registration_data']['event_title'] = "Event Registrations" # Fallback title
            else:
                messages.error(request, api_data.get('message_text', 'API returned a failure code.'))
        else:
            messages.error(request, f"API server error. Status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        messages.error(request, f"Error connecting to the API: {e}")

    return render(request, "events/view_registrations.html", context)



def public_registration_page(request, event_id):
    """
    Renders the public-facing registration page for a specific event.
    The form itself is built dynamically by JavaScript in the template.
    """
    context = {
        'event_id': event_id
    }
    return render(request, "events/public_registration_form.html", context)