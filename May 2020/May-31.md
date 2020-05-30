### Week April 26, 2020

- How Mock Framework works (Proxy based)
    - When do the unit test for project, most of time our code depends on other class or logic and sometimes it is complicated to manually create all the depended instance and pass them to our unit, that's why we us mock. Mock frameworks allow us to create fake objects and set it to return values or handle logics that we expect. Here is a example of the usage of this kind of framework.
    ```Java
    Foo foo = Mockito.mock(Foo.class);
    Mockito.when(foo.echo("foo")).thenReturn("foo");
    // Next time when we call foo.echo("foo") in our code, it will just return "foo"
    ```
    - Most of these frameworks are based on Proxy (that why I've covered Proxy and Reflection before). Also, since Proxy in class have some limitation, these frameworks use some code generation library to generate the bytecode of the proxy class. Unfortunately, I am not familiar with those libraries, so I will just use Java Proxy as example.
    - For Proxy based mock frameworks, we usually don't need to create the original object and wrap a proxy class around it, we just need to create a proxy class that has all the same functions as the original object. Here is a example of how to create a mock object using Java Proxy:
    ```Java
    public class Mock {
        public static <T> T mock(Class<T> clazz) {
            MockInvocationHandler invocationHandler = new MockInvocationHandler();
            // This MockInvocationHandler will intercept all function calls and handle itself.
            T proxy = (T) Proxy.newProxyInstance(Mock.class.getClassLoader(), new Class[]{clazz}, invocationHandler);
            return proxy;
        }
    }
    ```
    - Then the remaining question is how to implement this magical line:
    ```Java
    Mockito.when(foo.echo("foo")).thenReturn("foo");
    ```
    - It is quite easy to understand as we can read it like a sentence, it tells us when we call `foo.echo("foo")`, it will just return string `foo`. But how can we actually implement it? for the `when()` function, we know that when it is called, function call `foo.echo("foo")` has already returned, how can `when()` knows what function was called with what parameters?
    - The magic is that we are using the side effect of the function call: when we call some functions in mock object, it will just use some static fields to cache the method and parameters, what `when()` needs is just a type of the return value so that it can match the mock function call with our desired return value.
    - Remember in Java Proxy, all calls will be redirected to this `invoke` function below:
    ```Java
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        // param method tells us which function is called. In our case, it tells us echo() is called.
        // param args tells us what are the parameters of this function call. In our case, it tells us there is a "foo"

        // We can store this <method, params> pair into a self-defined data structure and wait for thenReturn being called.

        // Another case is that we are actually using this method, not setting the mock. So once we have the <method, params> pair, we need to first query if it exists, if it exist, we will just return the stored value.
    }
    ```
    - I've only mentioned the really really basic concept of proxy based mock frameworks and the real framework is way more complicated than this, but the similar idea of these framework is to handle most of the logic in the proxy function call (e.g. set desired return value, return desired value and assert # of times function is called).


##### reference:
http://blog.rseiler.at/2014/06/explanation-how-proxy-based-mock.html