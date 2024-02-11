import Alpine from 'alpinejs';
import { ValidationDsrcForm } from '../../../ext/ajv.validations';

function DsrcForm(formId, formData) {
	return {
		form: {},
		errors: [],
		ajvValidate: ValidationDsrcForm,
		async init() {
			if (!formData) {
				// We shouldn't reach this state: the data should be available, or the server should have returned an error before reaching this point and the form should not have been rendered
				console.error('Error fetching form data');
			}
			if (formData.errors) {
				// We shouldn't reach this state: AJV validation should have prevented form submission
				console.error('Error validating form data with AJV');
			} else {
				// There are no errors: This is a blank form
				const fields = Object.keys(formData);
				fields.forEach((field) => {
					this.form[field] = { ...formData[field], errors: [], touched: false };
				});
			}
			this.$nextTick(() => {
				// enable form validation for all submission types (click, keyboard, ...)
				document.getElementById(formId).addEventListener('submit', (event) => {
					this.validate();
					if (Array.isArray(this.errors) && this.errors.length > 0) {
						event.preventDefault();
					}
				});
			});
			// Disable browser validation as we are using our own
			document.getElementById(formId).setAttribute('novalidate', '');
			// Let the server know that JS is enabled
			document.getElementById(`${formId}_js_enabled`).value = 'true';
		},
		validate(event) {
			// debug
			const fields = Object.keys(this.form);
			const validateMap = {};
			fields.forEach((field) => {
				validateMap[field] = this.form[field].value;
			});
			let valid = this.ajvValidate(validateMap);
			if (!valid) {
				this.errors = this.ajvValidate.errors;
			} else {
				this.errors = [];
			}
		},
		getFieldErrors(fieldName) {
			const errors = this.errors.filter((error) => error.instancePath.substring(1) === fieldName);
			return errors.map((error) => error.message);
		},
		fieldHasError(fieldName) {
			const field = this.form[fieldName];
			return field.touched === true && field.errors.length > 0;
		},
		validateInput(event) {
			const field = event.target.name;
			this.validate();
			this.form[field].errors = this.getFieldErrors(field);
			if (this.form[field].is_valid === false && this.form[field].errors.length === 0) {
				this.form[field].is_valid = true;
				this.form[field].valid_class = 'valid';
			} else if (this.form[field].errors.length > 0) {
				this.form[field].is_valid = false;
				this.form[field].valid_class = 'error';
			}
		},
		touchInput(event) {
			const field = event.target.name;
			this.form[field].touched = true;
		},
		changeInput(event) {
			const field = event.target.name;
			this.form[field].changed = true;
		}
	};
}

Alpine.data('DsrcForm', DsrcForm);
