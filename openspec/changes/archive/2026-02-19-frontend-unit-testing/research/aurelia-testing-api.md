# Aurelia 2 Testing API Reference

Source: https://docs.aurelia.io/developer-guides/overview/testing-components

## createFixture API

```typescript
createFixture(
  template: string,           // HTML template with component usage
  appClass: any,             // App component class with test data
  components: any[],         // Components to register
  registrations?: any[]      // Optional DI registrations
)
```

### Return Object
- `appHost` - DOM container for rendered component
- `startPromise` - Promise resolving when component renders
- `started` - Awaitable shorthand (returns the fixture)
- `stop(true)` - Cleanup function
- `component` - Direct access to component instance
- `getBy(selector)` - Query single element
- `getAllBy(selector)` - Query multiple elements
- `queryBy(selector)` - Query or null
- `trigger` - Fire events (`.click()`, `.keydown()`)
- `type(selector, text)` - Text input simulation
- `assertText()` / `assertClass()` / `assertValue()` - Assertion helpers
- `printHtml()` - Debug output

## Testing Patterns

### Simple Component Render Test
```typescript
it('renders content', async () => {
  const { appHost, startPromise, stop } = createFixture(
    '<my-component name.bind="testName"></my-component>',
    class App { testName = 'Alice'; },
    [MyComponent]
  );
  await startPromise;
  expect(appHost.textContent).toContain('Alice');
  await stop(true);
});
```

### Mocking Dependencies via DI
```typescript
import { Registration } from 'aurelia';

const mockService = { format: vi.fn().mockReturnValue('Formatted') };
const { appHost } = await createFixture(
  '<person-detail></person-detail>',
  class App {},
  [PersonDetail],
  [Registration.instance(PersonFormatter, mockService)]  // 4th param
).started;
```

### Testing Bindings
```typescript
const { component } = await createFixture(
  '<my-comp items.bind="itemList"></my-comp>',
  class App { itemList: any[] = []; },
  [MyComp]
).started;

component.itemList = [1, 2, 3];
await tasksSettled();
// Assert DOM updated
```

### Testing Lifecycle Hooks
```typescript
const spy = vi.spyOn(MyComp.prototype, 'attached');
const { startPromise, stop } = createFixture(
  '<my-comp></my-comp>', class App {}, [MyComp]
);
await startPromise;
expect(spy).toHaveBeenCalled();
await stop(true);
```

### Event Triggering
```typescript
fixture.trigger.click('button');
fixture.trigger.keydown('input', { key: 'Enter' });
```

## Key Utilities
- `tasksSettled()` - Wait for async queue to flush (import from `@aurelia/testing`)
- `Registration.instance(Token, mock)` - Register mock in DI container
- `setPlatform()` / `BrowserPlatform` - Bootstrap test environment

## Best Practices
1. Always `await startPromise` or use `.started` before assertions
2. Always `await stop(true)` for cleanup (prevents memory leaks)
3. Use `tasksSettled()` after state changes that trigger async updates
4. Mock only what's necessary
5. Group related tests with `describe` blocks
6. One assertion focus per test
