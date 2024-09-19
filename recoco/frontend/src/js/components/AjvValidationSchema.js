import Alpine from 'alpinejs';
import { schemaOnboardingStep1SignupFormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingSignupForm';
import { schemaOnboardingEmailFormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingEmailForm';
import { schemaOnboardingStep1SigninFormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingSigninForm';
import { schemaOnboardingStep2ProjectFormValidator } from '../utils/ajv/schema/ajv.schema.OnboardingProjectForm';
import { schemaOnboardingPrefillSetuserFormValidator } from '../utils/ajv/schema/ajv.schema.PrefillSetuserForm';
import { schemaPrefillProjectFormValidator } from '../utils/ajv/schema/ajv.schema.PrefillProjectForm';

/**
 * Component returning a AJV schema to validate form field.
 * @param {string} schemaValidatorName - The name of the schema validator.
 * @returns {object} - The AjvValidationSchema object.
 */
Alpine.data('AjvValidationSchema', (schemaValidatorName) => {
  const schemasValidator = {
    schemaOnboardingStep1SignupFormValidator,
    schemaOnboardingStep1SigninFormValidator,
    schemaOnboardingEmailFormValidator,
    schemaOnboardingStep2ProjectFormValidator,
    schemaOnboardingPrefillSetuserFormValidator,
    schemaPrefillProjectFormValidator,
  };
  return {
    schemaValidator: schemasValidator[schemaValidatorName],
  };
});
