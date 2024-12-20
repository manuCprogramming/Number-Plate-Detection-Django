from django.shortcuts import render, redirect
from .models import Plate
from .forms import PlateForm
import cv2

def home(request):
    return render(request, 'home.html')

def capture_plate(request):
    try:
        plate_number = None
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            raise Exception("Could not open video device")

        while True:
            ret, frame = cap.read()
            if not ret:
                raise Exception("Failed to read frame from webcam")

            cv2.imshow('frame', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                plate_number = 'ABC1234'  # Placeholder for actual license plate detection logic
                break

        cap.release()
        cv2.destroyAllWindows()

        if plate_number:
            if Plate.objects.filter(plate_number=plate_number).exists():
                plate = Plate.objects.get(plate_number=plate_number)
                return render(request, 'plate_info.html', {'plate': plate})
            else:
                return render(request, 'new_plate.html', {'plate_number': plate_number})
        else:
            return render(request, 'invalid_plate.html')

    except Exception as e:
        print(f"An error occurred: {e}")
        if 'cap' in locals():
            cap.release()
        cv2.destroyAllWindows()
        return render(request, 'invalid_plate.html')

def save_new_plate(request):
    if request.method == 'POST':
        form = PlateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = PlateForm(initial={'plate_number': request.GET.get('plate_number', '')})
    return render(request, 'new_plate.html', {'form': form})