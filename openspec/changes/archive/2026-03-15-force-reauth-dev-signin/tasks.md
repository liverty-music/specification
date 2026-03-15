## Tasks

### Frontend

- [x] **FE-1**: Add environment-aware `prompt` parameter to `signIn()` in `auth-service.ts`
  - Pass `prompt: 'login'` when `import.meta.env.DEV` is true
  - No parameter in production (existing behavior preserved)
