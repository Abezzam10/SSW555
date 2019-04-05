# Coding Style Specification and Naming Pattern Guide Line

> This file aims at making the code neat and readable, and keeping everybody on the same page.

## Coding Guide Line

Python itself has a official coding style guideline [PEP8](https://www.python.org/dev/peps/pep-0008/), I suggest we try our best to code along with this guideline. There are plugins in VS Code market place that helps you keep the code in one style, feel free to try it out.

## Naming Pattern for the User Stories implementation

People's coding style varies from one another, it actually doesn't matter that much as long as we get the job done. But one thing I really suggest us to do, for the purposes of maintenablitiy and readability, is to come up with an agreement on how should we define our APIs, i.e. the name of the feature we implement in code.

Let's make an agreement on **how should we name the methods/functions we implement**.

Here by I will put my thoughts on the table, **please feel free to express your opinion either here our in emails**.

### Assumption

Assuming that we have a user story, whose info is listed as below:

- ID: US65536
- Name: Auto Code
- Descripsion: After we implement the code of this feature, the rest of the code will be automatically finished  :stuck_out_tongue: 
- The owner of this user story is **Benji**, he implemented this user story on **Feb 31st, 9999**.

### Give it a meaningful name and put info in `__doc__`

Based on the user story above, we should define the method as follow:

```python
class SomeClass:
    ...
    
    # here we are defining the method
    def us65536_auto_code(*args, **kwargs):
        """ Benji, Feb 31st, 9999
            Auto Code
            After we implement the code of this feature, the rest of the code will be automatically finished
            and split the descripsion with newline if it's too long.
        """
        your code
```

---

Please feel free to contibute your opinions!

---
