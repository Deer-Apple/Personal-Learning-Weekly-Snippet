### Week April 26, 2020

- Java Class (java.lang.class)
    - Normally we define a Java class (e.g. Cinema) in .java file, then it got compiled and output a .class file. In this .class file, there is a Class ojbect. 
    - Why we need this Class object? Just like we need a instruction book to build a Lego, JVM needs to know enough information about how to construct it. So when we want to `new` an Object, JVM will load the corresponding Class Object through Classloader then JVM will create the new instance based on the information it get from Class Object.
    - Note: we can create as many instance as we want for a single class that we've defined, but there is always only one Class object for every class
    - Examples about how to get the Class object (I am not going to discuss the pros and cons for these three way)
    ```Java
    // assume we have a class called Cinema
    // 1. we need to create an instance
    Cinema cinema = new Cinema();
    Class clazz = cinema.getClass();
    // 2. no need to create an instance
    Class clazz = Class.forName("{package}.Cinema");
    // 3. no need to create an instance
    Class clazz = Cinema.class;
    ```
- Java Reflection
    - Java Reflection makes it possible to inspect classes, interfaces, fields and methods at runtime, without knowing the names of the classes, methods etc. at compile time. It is also possible to instantiate new objects, invoke methods and get/set field values.
    - Java Reflection largely relies on the Class object for each class.
    - Here is some examples about basic usage.
    ```Java
    // assume we have a Cinema class
    class Cinema {
        public String cinemaName;
        public Cinema(String cinemaName) {
            this.cinemaName = cinemaName;
        }
        public void playMovie(String movieName) {
            System.out.println(cinemaName + " is playing " + movieName);
        }
    }
    Class clazz = Cinema.class;
    // 1. construct a Cinema object
    Constructor ctor = clazz.getDeclaredConstructor(String.class);
    Cinema cinema = (Cinema) ctor.newInstance("WanDa");
    // 2. invoke the playMovie method
    Method method = clazz.getDeclaredMethod("playMovie", String.class);
    method.invoke(cinema, "Star War");
    ```
    - A very simple use case is Apache Dbutils library. Instead of returning the ResultSet, it is able automatically fill in data in each row into an Java Object.
- How Java Reflection works
    - In this section, I will try to explain how Java Reflection works by looking into the source code, but it is just for the basic idea.
    - First, for `getDeclaredMethod`, it will search in the Class object to find the right method (same name, same parameters). The key data structure here is called `ReflectionData`, it stores all the information for the java class like `declaredFields`, `declaredConstructors` and `declaredPublicMethods`.
    - Second, once we have the method, we can invoke this method. If we step into the function, we will see there is a `MethodAccessor` object which calls its `invoke` method. `MethodAccessor` is actually an interface and we can say it has two version of implementations, one is native version and another one is Java version. For the first few times, it will use the native version and once it exceeds a threshold, it will change to Java bytecode version (the reason here is for time efficiency).
    - Conclusion: 
        - I've checked several functions (incl. `getDeclaredConstructor()`, `newInstance()`, `getDeclaredMethod()`, `invoke()`).
        - When we try to get a method or a constructor using Reflection, it will find the corresponding method or constructor from `ReflectionData` and return a copy of that.
        - When we try to invoke the method or use the constructor to init a object, it is actually called with the same functoin signature in `XXXAccessor` interface (e.g. `invoke()` in `MethodAccessor` and `newInstance` in `ConstructorAccessor`). Also, there is a Proxy Pattern here. The actual return value is a `DelegatingXXXAccessorImpl` and it can switch the actual implementation from native code to bytecode version based on some threshold. 

- What is Java Dynamic Proxy & How it works
    - What is Proxy Pattern
        - We create and use proxy objects when we want to add or modify some functionality of an already existing class. The proxy object is used instead of the original one. Usually, the proxy objects have the same methods as the original one. One example is static proxy.
    - Static Proxy
        - For static proxy, we need to manually create the proxy class. Usually,both target class and proxy class will implement the same interfaces or have the same methods. Here is an simple example.
        ```Java
        public interface Cinema {
            void playMovie(String name);
        }

        public class CinemaImpl implements Cinema {
            void playMovie(String name) {
                System.out.println("Playing movie: " + name);
            }
        }

        public class CinemaProxy implements Cinema {
            public Cinema target;
            public CinemaProxy(Cinema target) {
                this.target = target;
            }
            public playMovie(String name) {
                System.out.println("Showing pre-movie advertisement");
                target.playMovie(name);
                System.out.println("Showing post-movie advertisement");
            }
        }
        ```
        - We always need to define the java proxy class before running our program because JVM needs to load the corresponding Class object to create proxy class instance.
    - Dynamic proxy
        - From the discussion above, we know that in order to get the proxy class, we always need its Class object. For static proxy, we define the class and get it compiled. In contrast with static proxy, dynamic proxy generates bytecode for the proxy class, then initialized the proxy object using Java reflection at runtime. With the dynamic approach you don't need to create the proxy class, which can lead to more convenience. Here is a example of how to use Java Dynamic Proxy API.
        ```Java
        public interface Cinema {
            void playMovie(String name);
        }

        public class CinemaImpl implements Cinema {
            void playMovie(String name) {
                System.out.println("Playing movie: " + name);
            }
        }

        public class CinemaHandler implements InvocationHandler {
	        private Cinema target;
	        public PersonHandler(Ciname target){
		        this.target = target;
	        }
	        @Override
	        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
		        System.out.println("before....");
		        method.invoke(target, args);
		        System.out.println("after....");
		        return result;
	        }
        }

        public static void main(String[] args) {
            Cinema cinema = new CinemaImpl();

            Cinema proxy = (Cinema) Proxy.newProxyInstance(cinema.getClass().getClassLoader(), cinema.getClass().getInterfaces(), new CinemaHandler(cinema));

            proxy.playMovie("Star War");
        }
        ```
    - How Java Dynamic Proxy works (simple view)
        - `Proxy` and `InvocationHandler` are the main classes to provide Dynamic Proxy functionalities. We call `Proxy.newProxyInstance` static function to get the proxy object and pass an `InvocationHandler` instance to it. All the function calls in orignal object will be redirect to `invoke` method.
        - Inside `newProxyInstance`, it constructs the Class object by manually writing bytecode, then it returns the `Constructor<?>` object so that later we can create the proxy object just like normal Java Reflection code.
        - One question is that why we can directly cast the generated proxy class to target's type.
            - Note that Java Dynamic Proxy only works on **interfaces** and cannot work on concrete class. The generated proxy class will implements all the interfaces that the target implements and that's why we can do the cast.
        - Another question is in the proxy class, how to pass every function to the `InvocationHandler`. There are several steps.
            1. The generated proxy not only implements all target's interfaces, it also extends the `Proxy` class. In the `Proxy` class, it has a constructor with one `InvocationHandler` parameter. In last section, in order to create the proxy object, we get a `Constructor<?>` object and the parameter of this object is just one `InvocationHandler`. When we use reflection to invoke the constructor, we pass our custom `InvocationHandler` to it, so the proxy class now has the handler.
            2. When we call some methods on proxy object, it will just feed the corresponding parameters to call the `invoke` method on our handler.
        - Here is an example of generated proxy class
        ```Java
        public final class $Proxy11 extends Proxy implements Cinema {
            private static Method m1;
            private static Method m2;
            private static Method m3;
            private static Method m0;

            public $Proxy11(InvocationHandler var1) throws  {
                super(var1);
            }

            public final boolean equals(Object var1) throws  {
                try {
                    return ((Boolean)super.h.invoke(this, m1, new Object[]{var1})).booleanValue();
                } catch (RuntimeException | Error var3) {
                    throw var3;
                } catch (Throwable var4) {
                    throw new UndeclaredThrowableException(var4);
                }
            }

            public final String toString() throws  {
                try {
                    return (String)super.h.invoke(this, m2, (Object[])null);
                } catch (RuntimeException | Error var2) {
                    throw var2;
                } catch (Throwable var3) {
                    throw new UndeclaredThrowableException(var3);
                }
            }

            public final void playMovie() throws  {
                try {
                    super.h.invoke(this, m3, (Object[])null);
                } catch (RuntimeException | Error var2) {
                    throw var2;
                } catch (Throwable var3) {
                    throw new UndeclaredThrowableException(var3);
                }
            }

            public final int hashCode() throws  {
                try {
                    return ((Integer)super.h.invoke(this, m0, (Object[])null)).intValue();
                } catch (RuntimeException | Error var2) {
                    throw var2;
                } catch (Throwable var3) {
                    throw new UndeclaredThrowableException(var3);
                }
            }

            static {
                try {
                    m1 = Class.forName("java.lang.Object").getMethod("equals", Class.forName("java.lang.Object"));
                    m2 = Class.forName("java.lang.Object").getMethod("toString");
                    m3 = Class.forName("UserService").getMethod("playMovie");
                    m0 = Class.forName("java.lang.Object").getMethod("hashCode");
                } catch (NoSuchMethodException var2) {
                    throw new NoSuchMethodError(var2.getMessage());
                } catch (ClassNotFoundException var3) {
                    throw new NoClassDefFoundError(var3.getMessage());
                }
            }
        }
        ```


##### reference:
https://www.jianshu.com/p/3ea4a6b57f87 (Chinese)

https://blog.csdn.net/javazejian/article/details/70768369 (Chinese)

https://blog.csdn.net/lz710117239/article/details/78658168 (Chinese)