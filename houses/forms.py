from django import forms
from .models import House, Reservation

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_ADDITIONAL_IMAGES = 10


def validate_image_size(image):
    if image.size > MAX_IMAGE_SIZE:
        raise forms.ValidationError(
            "Image file must be smaller than 5 MB."
        )


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):


    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            "widget",
            MultipleFileInput()
        )
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):

        if isinstance(data, (list, tuple)):

            if len(data) > MAX_ADDITIONAL_IMAGES:
                raise forms.ValidationError(
                    f"You can upload a maximum of "
                    f"{MAX_ADDITIONAL_IMAGES} additional images."
                )

            cleaned_files = []

            for file in data:
                cleaned_file = super().clean(file, initial)

                validate_image_size(cleaned_file)

                cleaned_files.append(cleaned_file)

            return cleaned_files

        if data:
            cleaned_file = super().clean(data, initial)

            validate_image_size(cleaned_file)

            return [cleaned_file]

        return []

class HouseForm(forms.ModelForm):

    image = forms.ImageField(
        validators=[validate_image_size],
        widget=forms.ClearableFileInput(
            attrs={
                "accept": "image/*"
            }
        )
    )

    additional_images = MultipleImageField(
        required=False,
        label="Additional photos",
        widget=MultipleFileInput(
            attrs={
                "accept": "image/*"
            }
        )
    )

    class Meta:
        model = House

        fields = [
            "title",
            "description",
            "location",
            "price",
            "bedrooms",
            "bathrooms",
            "guests",
            "image",
        ]


class ReservationForm (forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            "check_in",
            "check_out",
            "guests",
        ]

        widgets = {
            "check_in": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "check_out": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                }
            ),

            "guests": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 1
                }
            ),
        }

    def __init__(self, *args, house=None, **Kwargs):
        super().__init__(*args, **Kwargs)
        self.house = house

        if house:
            self.fields["guests"].widget.attrs["max"] = house.guests

    def clean(self):

        cleaned_data = super().clean()

        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")
        guests = cleaned_data.get("guests")

        if check_in and check_out:

            if check_out <= check_in:
                raise forms.ValidationError(
                    "Check-out must be after check-in."
                )

            if self.house and guests:

                if guests > self.house.guests:
                    raise forms.ValidationError(
                        f"This house allows a maximum of "
                        f"{self.house.guests} guests"
                    )

        return cleaned_data
