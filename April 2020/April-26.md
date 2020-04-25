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


reference:
https://www.jianshu.com/p/3ea4a6b57f87 (Chinese)
https://blog.csdn.net/javazejian/article/details/70768369 (Chinese)