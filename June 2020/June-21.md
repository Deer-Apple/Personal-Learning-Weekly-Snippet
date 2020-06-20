### Week June 7, 2020

- Add AOP feature to the Java Web Framework
    - What is AOP
        - aspect-oriented programming (AOP) is a programming paradigm that aims to increase modularity by allowing the separation of cross-cutting concerns. It does so by adding additional behavior to existing code (an advice) without modifying the code itself, instead separately specifying which code is modified via a "pointcut" specification, such as "log all function calls when the function's name begins with 'set'". This allows behaviors that are not central to the business logic (such as logging) to be added to a program without cluttering the code, core to the functionality.
        - Use Case:
            1. Consider that we want to log the execution time for every function in our Java web application. If we manually add code in every function, it will be a huge work. But we can define a 'pointcut' to enhance/wrap all our function with execution time calculation code (might be hard to understand without code and example....).
    - Design goal
        ```Java
        @Aspect(Controller.class)
        public class ControllerAspect extends AspectProxy {
            private long begin;

            @Override
            public void before(Class<?> clazz, Method method, Object[] params) throws Throwable {
                begin = System.currentTimeMillis();
            }

            @Override
            public void after(Class<?> clazz, Method method, Object[] params, Object result) throws Throwable {
                LOGGER.debug(String.format("class: %s", clazz.getName()));
                LOGGER.debug(String.format("method: %s", method.getName()));
             LOGGER.debug(String.format("time: %dms", System.currentTimeMillis() - begin));
            }
        }
        ```
        Annotation `@Aspect(Controller.class)` tells us we want to define a aspect for evert method in Controller class (this is a annotation that you can find in my last snippet). There are also two method called `before` and `after` which will execute before controller's method and after controller's method to help us log the execution time.
    - Design detail
        1. Define a Aspect annotation
            ```Java
            @Target(ElementType.TYPE)
            @Retention(RetentionPolicy.RUNTIME)
            public @interface Aspect {
                Class<? extends Annotation> value();
            }
            ```
            The value here will tell us what kind of bean we want to enhance (e.g. Controller or Service).
        2. Define a Proxy interface
            ```Java
            public interface Proxy {
                Object doProxy(ProxyChain proxyChain) throws Throwable;
            }
            ```
            Since we might we want enhance the target class by several times, we need a chain to process it (e.g. log exec time & database transaction).
        3. Define ProxyChain
            ```Java
            public class ProxyChain {
                // ...

                public ProxyChain(Class<?> targetClass, Object targetObject, Method targetMethod, MethodProxy methodProxy, Object[] methodParams, List<Proxy> proxyList) {
                // ...
                }

                public Object doProxyChain() throws Throwable {
                    Object methodResult;
                    if (proxyIndex < proxyList.size()) {
                        methodResult = proxyList.get(proxyIndex++).doProxy(this);
                    } else {
                        methodResult = methodProxy.invokeSuper(targetObject, methodParams);
                    }
                    return methodResult;
                }
            }
            ```
            Almost all parameters are passed from CGlib (a code generation lib that can create a proxy class for normal java class). `proxyIndex` is used to check whether we have called all the proxy, if yes, we will use `methodProxy.invokeSuper()` to call the original method.
        4. Define a ProxyManager (create proxy class)
            ```Java
            public class ProxyManager {
                @SuppressWarnings("unchecked")
                public static <T> T createProxy(final Class<?> targetClass, final List<Proxy> proxyList) {
                    return (T) Enhancer.create(targetClass, (MethodInterceptor) (targetObject, targetMethod, methodParams, methodProxy) -> new ProxyChain(targetClass, targetObject, targetMethod, methodProxy, methodParams, proxyList).doProxyChain());
                }
            }
            ```
            It will just use CGlib to create proxy class and use these proxy (enhanced) class to replace orignal class(bean).
        5. Define a AspectProxy template
            ```Java
            public abstract class AspectProxy implements Proxy 

                @Override
                public Object doProxy(ProxyChain proxyChain) throws Throwable {
                    Object result;

                    Class<?> clazz = proxyChain.getTargetClass();
                    Method method = proxyChain.getTargetMethod();
                    Object[] params = proxyChain.getMethodParams();

                    begin();
                    try {
                        if (intercept(clazz, method, params)) {
                            before(clazz, method, params);
                            result = proxyChain.doProxyChain();
                            after(clazz, method, params, result);
                        } else {
                            result = proxyChain.doProxyChain();
                        }
                    } catch (Exception e) {
                        error(clazz, method, params, e);
                        throw e;
                    } finally {
                        end();
                    }
                    return result;
                }

                public void begin() {}

                public boolean intercept(Class<?> clazz, Method method, Object[] params) throws Throwable {
                    return true;
                }

                public void before(Class<?> clazz, Method method, Object[] params) throws Throwable {}

                public void after(Class<?> clazz, Method method, Object[] params, Object result) throws Throwable {}

                public void error(Class<?> clazz, Method method, Object[] params, Throwable e) {}

                public void end() {}
            }
            ```
            We define several empty hook method (`begin()`, `after()`) so the concrete class can override them. Just like the example in design goal, we will just override those method that we want to enhance our actual method.
        - Load the whole things
            - we first want to know scan all classes with `@Aspect` annotation to get a mapping of `<aspect, targetClass>`
            - then from the above map, we can get another mapping of `<targetClass, List<Proxy>>` (note that aspect are just the implementations of Proxy interface)
            - Create proxy class based on this Proxy list (which is just the last param when we construct ProxyChain) and use proxy class to replace the actual target class.
    - Conclusion
        1. <b>tl;dr</b> AOP is a just feature based on proxy, we create proxy class to replace actual class, so every time we want to execute a method, it will be intercepted and do those AOP logic around the actual logic.
        2. In my humble opinion, the real difficulty here is how to exec a chain of proxy and that's why I think the design of ProxyChain is brilliant. When the method is intercepted, we call  `proxyChain.doProxyChain()` and in that function, we will call `proxy.doProxy(this)` to exec the proxy logic and in proxy, it will call `proxyChain.doProxyChain()` back to start the next proxy (like a DFS).
            ```Java
            doProxyChain()
                -> doProxy1()
                    -> before1()
                    -> doProxyChain()
                        -> doProxy2()
                            -> before2()
                            -> doProxyChain()
                                -> invokeSuper()
                            -> after2()
                    -> after1()
            ```