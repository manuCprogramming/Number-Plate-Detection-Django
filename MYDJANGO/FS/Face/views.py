from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import View
from .models import LicensePlate
from .forms import LicensePlateForm
import cv2
import pytesseract
import numpy as np
from django.http import HttpResponse
from datetime import datetime, timedelta

def home(request):
    return render(request, 'home.html')

def validate_plate(request):
    if request.method == "POST":
        plate_number = request.POST.get('plate_number')
        try:
            plate = LicensePlate.objects.get(plate_number=plate_number)
            return render(request, 'license_info.html', {'plate': plate})
        except LicensePlate.DoesNotExist:
            if is_valid_plate_number(plate_number):
                return render(request, 'manual_entry.html', {'plate_number': plate_number})
            else:
                return render(request, 'invalid_plate.html')
    return redirect('home')

def open_webcam(request):
    if request.method == "POST":
        plate_number = capture_plate_number()
        if plate_number:
            try:
                plate = LicensePlate.objects.get(plate_number=plate_number)
                return render(request, 'license_info.html', {'plate': plate})
            except LicensePlate.DoesNotExist:
                if is_valid_plate_number(plate_number):
                    return render(request, 'manual_entry.html', {'plate_number': plate_number})
                else:
                    return render(request, 'invalid_plate.html')
    return redirect('home')

def is_valid_plate_number(plate_number):
    # Placeholder for actual plate number validation logic
    return True

def capture_plate_number():
    # Initialize the webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return None

    # Read a frame from the webcam
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame")
        cap.release()
        return None

    # Release the webcam
    cap.release()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise and improve OCR accuracy
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use Canny Edge Detection to detect edges in the image
    edged = cv2.Canny(blurred, 30, 200)

    # Find contours in the edged image
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Loop through the contours to find a rectangular one (assuming it is the plate)
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.018 * cv2.arcLength(contour, True), True)
        if len(approx) == 4:
            screenCnt = approx
            break
    else:
        print("No contour found")
        return None

    # Mask the rest of the image except the plate
    mask = np.zeros(gray.shape, np.uint8)
    new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1)
    new_image = cv2.bitwise_and(frame, frame, mask=mask)

    # Crop the plate part from the image
    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    cropped = gray[topx:bottomx+1, topy:bottomy+1]

    # Use Tesseract to extract text from the cropped image
    plate_text = pytesseract.image_to_string(cropped, config='--psm 8')

    return plate_text.strip()

def add_plate_info(request):
    if request.method == "POST":
        form = LicensePlateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = LicensePlateForm()
    return render(request, 'manual_entry.html', {'form': form})

def about_us(request):
    return render(request,'about_us.html')

def hsrp_registration(request):
    return render(request,'hsrp_registration.html')

def future_enhancements(request):
    return render(request,'future_enhancements.html')


def hours_ahead(request, offset):
    try:
        offset = int(offset)  # Convert the offset from string to integer
    except ValueError:
        raise Http404("Invalid hour offset")
    dt = datetime.now() + timedelta(hours=offset)
    html = f"<html><body >In {offset} hour(s), it will be {dt}.</body></html>"
    return HttpResponse(html)

def save_plate_info(request):
    if request.method == 'POST':
        plate_number = request.POST.get('plate_number')
        name = request.POST.get('name')
        rc_number = request.POST.get('rc_number')
        place = request.POST.get('place')
        age = request.POST.get('age')
        vehicle_type = request.POST.get('vehicle_type')
        vehicle_name = request.POST.get('vehicle_name')
        mobile_number = request.POST.get('mobile_number')
        aadhar_number = request.POST.get('aadhar_number')
        image = request.FILES.get('image')

        # Save to database
        plate = LicensePlate.objects.create(
            plate_number=plate_number,
            name=name,
            rc_number=rc_number,
            place=place,
            age=age,
            vehicle_type=vehicle_type,
            vehicle_name=vehicle_name,
            mobile_number=mobile_number,
            aadhar_number=aadhar_number,
            image=image
        )

        return JsonResponse({'plate': {
            'plate_number': plate.plate_number,
            'name': plate.name,
            'rc_number': plate.rc_number,
            'place': plate.place,
            'age': plate.age,
            'vehicle_type': plate.vehicle_type,
            'vehicle_name': plate.vehicle_name,
            'mobile_number': plate.mobile_number,
            'aadhar_number': plate.aadhar_number,
            'image': plate.image.url if plate.image else None
        }})
    return render(request, 'manual_entry.html')

class LicenseInfoView(View):
    def get(self, request):
        return render(request, 'license_info.html')

    def post(self, request):
        plate_number = request.POST.get('plate_number')
        try:
            plate = LicensePlate.objects.get(plate_number=plate_number)
            return render(request, 'license_info.html', {'license_info': plate})
        except LicensePlate.DoesNotExist:
            return redirect(reverse('add_plate_info'))

class SaveAsPDFView(View):
    def get(self, request):
        plate_number = request.GET.get('plate_number')
        try:
            plate = LicensePlate.objects.get(plate_number=plate_number)
            context = {'license_info': plate}
            html = render_to_string('license_info_pdf.html', context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'filename="license_info.pdf"'
            weasyprint.HTML(string=html).write_pdf(response)
            return response
        except LicensePlate.DoesNotExist:
            return HttpResponse("License plate information not found.", status=404)






