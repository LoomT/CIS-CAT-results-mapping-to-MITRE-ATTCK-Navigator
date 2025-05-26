export default class AngularHook {
  constructor(targetWindow) {
    this.targetWindow = targetWindow;
    this.hooks = [];
    this.overrideReflect();
  }

  /**
   * Register a hook for a specific class/method combination
   * @param {string[]} prototypeMatchers - List of prototype functions the class must have
   * @param {string} methodName - The method to hook ('constructor' for constructor hooking)
   * @param {Function} hookFunction - Function to call on hook, receives (instance, originalArgs, originalMethod)
   */
  hook(prototypeMatchers, methodName, hookFunction) {
    this.hooks.push({
      prototypeMatchers,
      methodName,
      hookFunction,
    });
  }

  /**
   * Check if a constructor matches the prototype requirements
   */
  matchesPrototype(constructor, prototypeMatchers) {
    if (!constructor || typeof constructor !== 'function' || !constructor.prototype) {
      return false;
    }

    return prototypeMatchers.every(method =>
      typeof constructor.prototype[method] === 'function',
    );
  }

  /**
   * Create a proxy handler for the matched hook
   */
  createProxy(hook, constructor) {
    const self = this;

    if (hook.methodName === 'constructor') {
      /** Hook the constructor, we need to handle this specially because
       * the constructor == function in JS, so we cannot override the
       * constructor as obj.prototype.constructor = ...
       */
      return {
        construct: (target, argumentsList) => {
          const instance = Reflect.construct(target, argumentsList);
          hook.hookFunction(instance, argumentsList, target);
          return instance;
        },
      };
    }
    else {
      // Hook a specific method
      const originalMethod = constructor.prototype[hook.methodName];
      if (originalMethod) {
        constructor.prototype[hook.methodName] = function (...args) {
          const result = originalMethod.apply(this, args);
          hook.hookFunction(this, args, originalMethod);
          return result;
        };
      }
      return null;
    }
  }

  /**
   * Override Reflect.decorate to intercept class decorators
   */
  overrideReflect() {
    const self = this;
    /* In case */
    const originalDecorate = this.targetWindow.Reflect.decorate;

    this.targetWindow.Reflect.decorate = function decorate(
      decorators,
      target,
      propertyKey,
      desc,
    ) {
      let argCount = arguments.length;
      let result = argCount < 3
        ? target
        : desc === null ? (desc = Object.getOwnPropertyDescriptor(target, propertyKey)) : desc;

      // Check if this constructor matches any of our hooks
      for (const hook of self.hooks) {
        if (self.matchesPrototype(target, hook.prototypeMatchers)) {
          const proxy = self.createProxy(hook, target);
          if (proxy && hook.methodName === 'constructor') {
            target = new Proxy(target, proxy);
          }
        }
      }

      // Apply decorators from last to first (right-to-left)
      for (let i = decorators.length - 1; i >= 0; --i) {
        let decorator = decorators[i];
        if (!decorator) continue;

        if (argCount < 3) {
          // Class decorator signature:  (target) => newTarget | void
          result = decorator(result) || result;
        }
        else if (argCount > 3) {
          // Method/accessor/property decorator with descriptor: (target, key, desc) => newDesc | void
          result = decorator(target, propertyKey, result) || result;
        }
        else {
          // Method/accessor/property decorator without descriptor: (target, key) => void
          result = decorator(target, propertyKey) || result;
        }
      }

      // If we were decorating a property and ended with a descriptor, re-define it.
      if (argCount > 3 && result && Object.defineProperty) {
        Object.defineProperty(target, propertyKey, result);
      }

      return result;
    };
  }
}
