document.addEventListener('DOMContentLoaded', function () {
    const phoneInput = document.querySelector('#profile-phone-input');
    const profileForm = document.querySelector('#profile-edit-form');

    if (!phoneInput || !profileForm || !window.intlTelInput) {
        return;
    }

    const iti = window.intlTelInput(phoneInput, {
        initialCountry: 'bg',
        preferredCountries: ['bg', 'de', 'gb', 'us'],
        separateDialCode: true,
        nationalMode: true,
        autoPlaceholder: 'polite',
        utilsScript: 'https://cdn.jsdelivr.net/npm/intl-tel-input@25.3.1/build/js/utils.js',
    });

    profileForm.addEventListener('submit', function () {
        let fullPhoneNumber = iti.getNumber();

        if (!fullPhoneNumber) {
            const selectedCountry = iti.getSelectedCountryData();
            const localNumber = phoneInput.value.replace(/\D/g, '');

            if (selectedCountry && selectedCountry.dialCode && localNumber) {
                fullPhoneNumber = `+${selectedCountry.dialCode}${localNumber}`;
            }
        }

        if (fullPhoneNumber) {
            phoneInput.value = fullPhoneNumber.replace(/\s/g, '');
        }
    });
});