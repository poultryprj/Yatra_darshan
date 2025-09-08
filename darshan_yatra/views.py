
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
    api_url = "https://www.lakshyapratishthan.com/apis/routeyatradates"
    try:
        resp = requests.get(api_url, headers=headers, verify=False, timeout=10)
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
            api_url = "https://www.lakshyapratishthan.com/apis/searchregistrations"
            payload = {"search": mobile}
            response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

            if response.status_code != 200:
                return JsonResponse({"message_code": 999, "message_text": f"HTTP Error {response.status_code}"})
            
            data = response.json()
            if str(data.get("message_code")) == "1000":
                from datetime import datetime

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
                    blood_group_name = r.get("BloodGroup", "").strip()
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
                        "AreaId": r.get("AreaId"),  # 🔥 Make sure AreaId is included
                        "AreaName": r.get("AreaName"),
                        "Address": r.get("Address"),
                    })
                        
                return JsonResponse({"message_code": 1000, "message_text": "OK", "message_data": rows})

            return JsonResponse({"message_code": 999, "message_text": data.get("message_text", "No data")})

        elif action == "list_area":
            api_url = "https://www.lakshyapratishthan.com/apis/listarea"
            resp = requests.get(api_url, headers=headers, verify=False, timeout=10)
            return JsonResponse(resp.json(), safe=False, status=200 if resp.status_code == 200 else 500)

        elif action == "list_gender":
            api_url = "https://www.lakshyapratishthan.com/apis/listgender"
            resp = requests.get(api_url, headers=headers, verify=False, timeout=10)
            return JsonResponse(resp.json(), safe=False, status=200 if resp.status_code == 200 else 500)
        
        
        elif action == "book_ticket":
            try:
                user_id = request.POST.get("UserId")
                amount_paid = request.POST.get("AmountPaid")
                discount = request.POST.get("Discount", 0)
                discount_reason = request.POST.get("DiscountReason", "")
                payment_id = request.POST.get("PaymentId")
                bookings_json = request.POST.get("Bookings", "[]")

                import json
                bookings = json.loads(bookings_json)  # list of {RegistrationId, YatraIds}

                print("Booking Request →")
                print("UserId:", user_id)
                print("AmountPaid:", amount_paid)
                print("Discount:", discount)
                print("DiscountReason:", discount_reason)
                print("PaymentId:", payment_id)
                print("Bookings:", bookings)

                # TODO: Save or forward each booking
                # Example structure
                result = []
                for b in bookings:
                    result.append({
                        "RegistrationId": b["RegistrationId"],
                        "YatraIds": b["YatraIds"]
                    })

                return JsonResponse({
                    "message_code": 1000,
                    "message_text": "Tickets booked successfully",
                    "data": {
                        "UserId": user_id,
                        "Bookings": result,
                        "AmountPaid": amount_paid,
                        "Discount": discount,
                        "PaymentId": payment_id
                    }
                })

            except Exception as e:
                return JsonResponse({
                    "message_code": 999,
                    "message_text": f"Exception in booking: {str(e)}"
                })


        elif action == "list_bloodgroup":
            api_url = "https://www.lakshyapratishthan.com/apis/listbloodgroup"
            resp = requests.get(api_url, headers=headers, verify=False, timeout=10)
            return JsonResponse(resp.json(), safe=False, status=200 if resp.status_code == 200 else 500)

        elif action == "submit":
            api_url = "https://www.lakshyapratishthan.com/apis/pilgrimregistration"

            # Accept DD/MM/YYYY directly from client; if it arrives as yyyy-mm-dd, try to convert.
            dob_in = request.POST.get("DateOfBirth", "")
            dob_final = dob_in
            if dob_in and "-" in dob_in and "/" not in dob_in:
                try:
                    from datetime import datetime
                    dob_final = datetime.strptime(dob_in, "%Y-%m-%d").strftime("%d/%m/%Y")
                except Exception:
                    pass

            payload = {
                "RegistrationId": request.POST.get("RegistrationId", 0),
                "userMobileNo": request.POST.get("userMobileNo"),
                "userFirstname": request.POST.get("userFirstname"),
                "userMiddlename": request.POST.get("userMiddlename", ""),
                "userLastname": request.POST.get("userLastname"),
                "AreaId": request.POST.get("AreaId", 1),
                "Gender": request.POST.get("Gender", 1),
                "Address": request.POST.get("Address", ""),
                "userAlternateMobileNo": request.POST.get("userAlternateMobileNo", ""),
                "BloodGroup": request.POST.get("BloodGroup", "Select"),  # send text e.g., "O+"
                "DateOfBirth": dob_final,
                "Photo": request.POST.get("Photo", ""),
                "PhotoId": request.POST.get("PhotoId", ""),
                "UserId": str(request.session.get("user_id", 0)),
            }
            print("358", payload)
            resp = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)
            if resp.status_code != 200:
                return JsonResponse({"message_code": 999, "message_text": f"HTTP Error {resp.status_code}"})
            return JsonResponse(resp.json(), safe=False)

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


# userMobileNo:9850180648
# userPassword:999999