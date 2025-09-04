
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
    
    # Fetch user details from session
    user_details = {
        "first_name": request.session.get("first_name", ""),
        "last_name": request.session.get("last_name", ""),
        "mobile_no": request.session.get("mobile_no", ""),
        "aadhar_no": request.session.get("aadhar_no", ""),      
    }

    # Fetch Route Yatras
    route_yatras_data = []
    try:
        res = requests.get("https://www.lakshyapratishthan.com/apis/routeyatradates", timeout=5)
        if res.status_code == 200:
            json_data = res.json()
            route_yatras_data = json_data.get("message_data", [])
    except Exception as e:
        print("Error fetching route yatra:", e)

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
                mobile = request.POST.get("search")  # <-- read 'search' from POST
                api_url = "https://www.lakshyapratishthan.com/apis/searchregistrations"
                payload = {"mobile_no": mobile}
                response = requests.post(api_url, json=payload, headers=headers, verify=False, timeout=10)

            elif action == "list_area":
                api_url = "https://www.lakshyapratishthan.com/apis/listarea"
                response = requests.get(api_url, headers=headers, verify=False, timeout=10)

            elif action == "list_gender":
                api_url = "https://www.lakshyapratishthan.com/apis/listgender"
                response = requests.get(api_url, headers=headers, verify=False, timeout=10)

            elif action == "list_bloodgroup":
                api_url = "https://www.lakshyapratishthan.com/apis/listbloodgroup"
                response = requests.get(api_url, headers=headers, verify=False, timeout=10)

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





# userMobileNo:9850180648
# userPassword:999999