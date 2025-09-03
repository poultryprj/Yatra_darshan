
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
import requests
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://www.gyaagl.app",
    "Referer": "https://www.gyaagl.app/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')    
    
    if request.method == 'POST':
        print("24")
        mobile = request.POST.get('mobile')
        pin = request.POST.get('pin_number')
        api_url = 'https://www.lakshyapratishthan.com/apis/agentlogin'
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
                    user_info = data["message_text"][0]
                    request.session["user_id"] = user_info["UserId"]
                    request.session["first_name"] = user_info["UserFirstname"]
                    request.session["last_name"] = user_info["UserLastname"]
                    request.session["user_role"] = user_info["UserRole"]
                    return redirect('Registrationpage')
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

    # ✅ Prepare user details from session
    user_details = {
        "first_name": request.session.get("first_name", ""),
        "last_name": request.session.get("last_name", ""),
        "mobile_no": request.session.get("mobile_no", ""),
        "aadhar_no": request.session.get("aadhar_no", ""),
        "user_role": request.session.get("user_role", ""),
    }

    # ✅ Fetch Route Yatras using API (same style as login)
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
                        # Only fill fields if user exists
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
                }

                print("➡️ Calling:", api_url)
                print("➡️ Payload:", payload)

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


def logout(request):
    request.session.clear()  # Clears all session data, keeps same session key
    return redirect('login')    

# userMobileNo:9850180648
# userPassword:999999