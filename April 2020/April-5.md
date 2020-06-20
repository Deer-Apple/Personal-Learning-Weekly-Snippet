### Week April 5, 2020

- Java Servlet
    - when using vanilla Java Servlet to development Java web application, we need to create one servlet for each kind of http endpoint (e.g. one for "/customer" and one for "/account").
    - That's why we want to build some Java web framework which incorporates several related endpoints into one single `controller` class. For example,
    ```Java
    @controller
    public class CustomerController {

        @Inject
        private CustomerService customerService;

        @Action("get:/customer")
        public View getCustomer(Params params) {

        }

        @Action("get:/customers")
        public View getAllCustomers(Params params) {

        }

        @Action("post:/customer")
        public View createCustomer(Params params) {

        }
    }
    ```

- ThreadLocal
    - One common use case for ThreadLocal is for Database connection.
        - It is too expensive if we request a new database connection every time we want to execute a sql query. That's why we use a database connection pool to cache database connections (Apache DBCP).
        - We also want to make sure in one single thread, we always use the same connection in order to maintain the sql transaction.
    - Implementation
        - The secret is in `Thead` class. There is a field called `threadLocals` with type `ThreadLocalMap` which is actually a hashmap of `<threadlocal, value>`
        - Every time we can `get/set` method on `ThreadLocal` object, it will first get current thread's map and search entry in it.
        ```Java
        Thread t = Thread.currentThread();
        ThreadLocalMap map = getMap(t);

        public ThreadLocaMap getMap(Thread t) {
            return t.threadLocals;
        }
        ```
    - What if we have several `ThreadLocal` objects in one class?
        - First, `threadLocals` in every thread is a hashmap (more precisely an array of entry whose key is threadlocal object)
        - Second, everytime a `ThreadLocal` object is constructed, it will also initialize a final field called `threadLocalHashCode` which is then used to calculate the corresponding index in the hashmap array.
    - Important Note:
        - When you are using a static field in your class, consider whether you need to distinguish this value between different threads, if yes, you probably want to use `ThreadLocal`

- WeekReference
    - An object with only weekreferences will be cleared by Grabage Collector.
    - As stated by Java documentation, weak references are most often used to implement canonicalizing mappings.
    - One example is the `ThreadLocalMap` in `TheadLocal` class. Here is how the Entry is defined in `ThreadLocal`
    ```Java
    static class Entry extends WeakReference<ThreadLocal<?>> {
        /** The value associated with this ThreadLocal. */
        Object value;

        Entry(ThreadLocal<?> k, Object v) {
            super(k);
            value = v;
        }
    }

    ```
    - When `entry.get() == null` means the corresponding `ThreadLocal` object is no longer exist so we can refill this index with new entry.

- Transient
    - Every field marked as `transient` will not be serialized. You use the `transient` keyword to indicate to the jvm that the `transient` variable is not part of the persistent state of an object. Which means we cannot retrieve that value after deseralization.

TODO(P1): read book <架构探险 从零开始写javaweb框架> to implement a lite version Java framework.