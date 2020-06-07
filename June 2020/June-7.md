### Week June 7, 2020

- Steps for building a simple Java Web framework (IoC)
    - Projet goal (version 1)
        ```Java
        @Controller
        public class HelloController {
            @Inject
            private GreetingService greetingService;

            @Action("get:/hello")
            public Data sayHello(Param param) {
                return new Data(greetingService.sayHello());
            }

            @Action("get:/bye")
            public Data sayBye(Param param) {
                return new Data(greetingService.sayBye());
            }
        }
        ```
        1. Previously, we can only handle one specific request path in one Servlet which means we need to create a lot of Servlets to hanle all the logics. In this framework, we are trying to group request paths that share similar logic in one controller class.
        2. With `@Inject` we are trying to let the framework initialize the Service for me. We don't need to explicitly create it and we can directly use it in the function.
        3. We store all request parameters in `Param` class, including query parameters and parameters in the request body and pass it to the function. We can retrieve one parameter by calling `param.getParam("XXX")`.
        4. We return a `Data` object which we just convert the return data into the json format.
    - Design detail
        1. Degine a configuration file (we are using the Maven project structure)
            - Users need to create a file named `smart.properties` under `src/main/resources`, so that we can read their configuration and override the framework default setup. One property that users must provide is the base package path
                ```Properties
                smart.framework.app.base_package_path=aaa.bbb.ccc
                ```
        2. Create a class loader
            - Based on the property file in last section, we know what is the base package path, then we can scan all the Java files and Jars under that path and find out all the classed with annotations like `@Controller`, `@Inject` and `@Action`.
            - We have four basic annotations:
                1. `@Controller` to annotate the controller classes, these classes handle request mapping and call corresponding services to execute actual business logic.
                2. `@Service` to annotate the service classes, these classes may connect with Database and do some CRUD.
                3. `@Inject` to annotate the service field in the controller and we can inject the actual service object into these fields.
                4. `@Action` to annotate a specific request path and request method.
            - we scan all files under base package path and store all `Class<?>` into a `CLASS_SET`. From this `CLASS_SET`, we can get all controller classes and service classes by filtering if they have the corresponding annotation like:
                ```Java
                for(Class<?> clazz : CLASS_SET) {
                    if (clazz.isAnnotationPresent(Controller.class));
                }    
                ```
        3. Implement Bean container (We see all the controller instances and service instances as that are maintained by this framework `Bean`)
            - We can use Java Reflection to create instances for our controller classes and service classes, then store them into a `HashMap<Class<?>,Object> BEAN_MAP`.
        4. Inject dependency
            - In last section, we've got all Beans from `BEAN_MAP`, note that some `Bean`s like controller may have some dependent service classes, so we need to manually set those fields also by Java Reflection. Basic concept is like this:
                ```Java
                for (Map.Entry<Class<?>,Object> entry : BEAN_MAP.entrySet()) {
                    Class<?> beanClass = entry.getKey();
                    Object beanInstance = entry.getValue();
                    for (Field beanField : beanClass.getDeclaredFields()) {
                        if (beanField.isAnnotationPresent(Inject.class)) {
                            // inject dependency
                        }
                    }
                }
                ```
        5. Analyze request path
            - All the supported request path are defined with annotation `@Action` in the controller class, so we want to analyze all supported request path and add a mapping from (request method + request path) to handler method. Here we need to define two class:
                1. Request class
                    ```Java
                    public class Request {
                        private String requestPath;
                        private String requestMethod;
                        // getter, setter ...
                    }
                    ```
                2. Handler class
                    ```Java
                    public class Handler {
                        private Class<?> controllerClass;
                        private Method actionMethod;
                    }
                    ```
            - We will just iterate all controller classes and find out all the method with annotation `@Action` so that we can get a `HashMap<Request,Handler> ACTION_MAP`.
        6. Define DispatcherServlet
            - I think this is how all our previous configuration and magic work. By defining a servlet that handles all the incoming request, we can make sure our framework will first get the request and then analyze it, send it to the corresponding method to handle it.
            - We also need to define several classes like `Data` and `Param`. `Data` will just convert the incoming object into a json and `Param` will just extract and store all the parameters in a request and pass them as the paramter for those action method.
            - Basic logic are as follows:
                ```Java
                @WebServlet(urlPatterns = "/*", loadOnStartup = 0)
                public class DispatcherServlet extends HttpServlet {
                    @Override
                    public void init(ServletConfig config) throws ServletException {
                        // init all above steps (1-5)
                    }

                    @Override
                    protected void service(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
                        // 1. get the correct handler
                        String requestMethod = req.getMethod().toLowerCase();
                        String requestPath = req.getPathInfo();
                        Request request = new Request(requestMethod, requestPath);
                        Handler handler = ACTION_MAP.get(request);
                        // 2. construct Param object
                        // ...
                        // 3. invoke action method
                        Method actionMethod = handler.getActionMethod();
                        Object result = ReflectionUtil.invokeMethod(controllerBean, actionMethod, param);
                        // 4. write response
                        // ...
                    }
                }
                ```
    - Why framework can work (could be wroing)
        - When tomcat run a Java web application, it will also scan Jars and class files. Since we are adding the `SmartFramework` as a dependency, our `DispatcherServlet` will be discovered and registered.



TODO(P1): Add repo pointer for smart framework.