"""Seed questions: Object-Oriented Programming (oop) across Python, JavaScript, PHP, C++ and General."""

from app.content.qdef import FB, Q

D = "oop"
PY = "python"
JS = "javascript"
PHP = "php"
CPP = "cpp"
JAVA = "java"
GEN = "general"

QUESTIONS_OOP = [
    # ── Python · Beginner ───────────────────────────────────────────────────
    Q(D, "beginner", PY, "A Counter class and two instances",
      """class Counter:
    def __init__(self):
        self.count = 0

    def step(self):
        self.count += 1

a = Counter()
b = Counter()
a.step()
a.step()
b.step()
print(a.count, b.count)""",
      "What does this program print, and why doesn't calling a.step() change b.count?",
      [("prints 2 1", ["2 1", "2 and 1"], 2),
       ("a and b are separate instances with their own self.count attribute", ["separate", "own", "independent", "instance", "two objects"], 1),
       ("__init__ sets self.count = 0 on each new instance", ["__init__", "self.count"], 1)],
      [("thinks count is shared between a and b (prints 3 3)", ["3 3"], "self.count is stored on each instance separately, not shared across the class.")],
      "It prints 2 1. Each Counter() call creates a separate instance and runs __init__, giving that object its own "
      "self.count starting at 0. Calling a.step() updates a.count twice (to 2), while b.step() updates b.count once (to 1)."),

    Q(D, "beginner", PY, "Forgetting self on an attribute",
      """class PiggyBank:
    def __init__(self):
        self.coins = 0

    def deposit(self, amount):
        coins = self.coins + amount

bank = PiggyBank()
bank.deposit(10)
print(bank.coins)""",
      "What does this print, why didn't bank.coins change, and how do you fix deposit?",
      [("prints 0", ["prints 0", "0", "still 0", "stays 0"], 2),
       ("coins = ... creates a local variable inside deposit instead of updating self.coins", ["local", "self.coins", "attribute", "discarded"], 1.5),
       ("fix: write self.coins = self.coins + amount (or self.coins += amount)", ["self.coins =", "self.coins +="], 1)],
      [("thinks it prints 10", ["prints 10"], "Bare coins inside deposit is a local variable that disappears when deposit returns; self.coins is untouched.")],
      "It prints 0. Inside deposit, assigning to bare coins creates a local variable that is discarded when the "
      "method returns; the instance attribute self.coins is never updated. Fix it by writing "
      "self.coins = self.coins + amount (or self.coins += amount)."),

    FB(D, "beginner", PY, "Missing code: store the constructor argument on self",
       """class Greeter:
    def __init__(self, name):
        ____

    def hello(self):
        return f"Hi, {self.name}!"

print(Greeter("Ada").hello())  # Hi, Ada!""",
       "Fill in the blank inside __init__ so hello() can read self.name.",
       ["self.name = name"],
       [("saves the parameter name onto the instance attribute self.name", ["instance", "attribute", "self.name", "parameter"], 1)],
       [("writes name = self.name", ["name = self.name"], "That reads self.name before it exists instead of storing the parameter on self.")],
       "The blank is self.name = name. Inside __init__, assigning to self.name attaches the parameter name as an "
       "instance attribute on the new Greeter object so hello() can read self.name."),

    # ── Python · Intermediate ───────────────────────────────────────────────
    Q(D, "intermediate", PY, "Inheritance and super().__init__",
      """class Account:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance

class SavingsAccount(Account):
    def __init__(self, owner, balance, rate):
        super().__init__(owner, balance)
        self.rate = rate

    def add_interest(self):
        self.balance += int(self.balance * self.rate)

acct = SavingsAccount("Lin", 100, 0.05)
acct.add_interest()
print(acct.owner, acct.balance)""",
      "What does this print, and what role does super().__init__(owner, balance) play?",
      [("prints Lin 105", ["lin 105"], 2),
       ("super().__init__ calls Account.__init__ to set self.owner and self.balance on the subclass instance", ["super", "parent", "account.__init__", "self.owner", "self.balance"], 1.5),
       ("add_interest adds 5% of 100 (5) to self.balance", ["105", "5%", "0.05"], 0.5)],
      [("thinks super() creates a separate Account object", ["two objects", "separate account"], "super().__init__ initializes the same self instance using the parent constructor.")],
      "It prints Lin 105. SavingsAccount inherits from Account; calling super().__init__(owner, balance) runs "
      "Account.__init__ on the same self instance to set self.owner = 'Lin' and self.balance = 100 before storing "
      "self.rate = 0.05. Then add_interest() adds 5 to self.balance."),

    Q(D, "intermediate", PY, "Class attribute vs instance attribute shadowing",
      """class User:
    role = "guest"

u1 = User()
u2 = User()
u1.role = "admin"
print(u1.role, u2.role, User.role)""",
      "What does this print, and why doesn't assigning u1.role = 'admin' change u2.role?",
      [("prints admin guest guest", ["admin guest guest"], 2),
       ("u1.role = 'admin' creates an instance attribute on u1 that shadows User.role", ["instance attribute", "shadow", "u1.__dict__", "own attribute"], 1.5),
       ("u2 has no instance attribute role so lookup falls back to the class attribute User.role", ["class attribute", "falls back", "user.role"], 1)],
      [("thinks u1.role changes User.role for all instances (prints admin admin admin)", ["admin admin admin"], "Assigning on u1 writes to u1's instance dictionary; it does not mutate User.role.")],
      "It prints admin guest guest. role = 'guest' is a class attribute on User. Assigning u1.role = 'admin' creates "
      "an instance attribute on u1 that shadows User.role for u1 only; u2 still has no instance attribute role, so "
      "u2.role resolves to User.role ('guest')."),

    FB(D, "intermediate", PY, "Missing code: call the parent constructor in Python",
       """class Vehicle:
    def __init__(self, brand):
        self.brand = brand

class ElectricCar(Vehicle):
    def __init__(self, brand, battery_kwh):
        ____
        self.battery_kwh = battery_kwh

car = ElectricCar("Rivian", 135)
print(car.brand, car.battery_kwh)  # Rivian 135""",
       "Fill in the blank so ElectricCar delegates brand initialization to Vehicle.",
       ["super().__init__(brand)", "Vehicle.__init__(self, brand)"],
       [("super().__init__(brand) invokes the parent class constructor on self", ["super", "parent", "vehicle", "constructor"], 1)],
       [("passes self to super().__init__", ["super().__init__(self, brand)"], "super() already binds self automatically; pass only brand.")],
       "The blank is super().__init__(brand). super() returns a proxy bound to self that calls Vehicle.__init__(self, brand) "
       "so self.brand is initialized before setting self.battery_kwh."),

    Q(D, "intermediate", PY, "Encapsulation with @property validation",
      """class Product:
    def __init__(self, price):
        self.price = price

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if value < 0:
            raise ValueError("price cannot be negative")
        self._price = value""",
      "How does @property protect the Product invariant, and what happens when Product(-5) is called?",
      [("Product(-5) raises ValueError immediately because self.price = price in __init__ runs the setter", ["valueerror", "raises", "__init__", "setter"], 2),
       ("@property and @price.setter intercept attribute reads and writes while keeping normal dot syntax", ["intercept", "getter", "setter", "dot syntax", "_price", "invariant"], 1.5)],
      [("thinks __init__ bypasses the setter", ["bypasses", "only after __init__"], "self.price = price inside __init__ goes through @price.setter just like any other assignment.")],
      "Product(-5) raises ValueError('price cannot be negative'). Because __init__ assigns to self.price (not "
      "self._price), the assignment runs @price.setter, enforcing the non-negative invariant both at construction "
      "time and on later updates while callers still use clean p.price dot syntax."),

    # ── Python · Advanced ───────────────────────────────────────────────────
    Q(D, "advanced", PY, "Shared mutable class attribute bug",
      """class Cart:
    items = []

    def add(self, item):
        self.items.append(item)

c1 = Cart()
c2 = Cart()
c1.add("book")
print(c2.items)""",
      "What does print(c2.items) output, why is this a bug, and how should Cart be written instead?",
      [("prints ['book']", ["['book']", '["book"]', "book"], 2),
       ("items = [] is a class attribute shared by every Cart instance and mutated in place by append", ["class attribute", "shared", "mutat", "in place", "same list"], 1.5),
       ("fix: initialize self.items = [] inside def __init__(self)", ["__init__", "self.items = []"], 1)],
      [("thinks c2.items is []", ["prints []", "empty list"], "self.items looks up Cart.items because no instance attribute exists, and .append() mutates that shared list.")],
      "It prints ['book']. items = [] is defined on the class body, so a single list object is shared across every "
      "Cart instance; self.items.append('book') mutates that shared list in place. Fix it by setting "
      "self.items = [] inside def __init__(self): so each Cart gets its own list."),

    Q(D, "advanced", PY, "Duck typing vs brittle isinstance chains",
      """def notify_all(channels, msg):
    for ch in channels:
        if isinstance(ch, EmailChannel):
            ch.send_email(msg)
        elif isinstance(ch, SmsChannel):
            ch.send_sms(msg)""",
      "Critique this design from an OOP perspective and explain how polymorphism / an abstract base class improves it.",
      [("adding a new channel forces editing notify_all (violates Open/Closed Principle)", ["open/closed", "modify notify_all", "every new", "brittle", "if/elif"], 2),
       ("give every channel a common send(msg) method (duck typing / ABC with @abstractmethod) and call ch.send(msg)", ["send(", "polymorph", "duck typing", "abstract", "common interface"], 1.5)],
      [],
      "notify_all is tightly coupled to every concrete class and violates the Open/Closed Principle: adding "
      "PushChannel requires modifying notify_all and its method names. Instead, define a uniform method contract "
      "send(self, msg) (via duck typing or an ABC with @abstractmethod) so notify_all simply calls ch.send(msg) "
      "polymorphically for any channel."),

    Q(D, "advanced", PY, "Diamond inheritance and Method Resolution Order (MRO)",
      """class A:
    def ping(self):
        return ["A"]

class B(A):
    def ping(self):
        return ["B"] + super().ping()

class C(A):
    def ping(self):
        return ["C"] + super().ping()

class D(B, C):
    def ping(self):
        return ["D"] + super().ping()

print(D().ping())""",
      "What does D().ping() return, and why does B's super().ping() call C.ping instead of A.ping directly?",
      [("returns ['D', 'B', 'C', 'A']", ["['d', 'b', 'c', 'a']", "d, b, c, a", '["d", "b", "c", "a"]'], 2),
       ("super() follows the C3 linearization / MRO of D (D -> B -> C -> A), not just B's static parent", ["mro", "linearization", "d -> b -> c -> a", "next in line"], 1.5),
       ("each class in the diamond runs exactly once", ["once", "diamond"], 1)],
      [("thinks it returns ['D', 'B', 'A']", ["['d', 'b', 'a']"], "In Python, super() delegates to the next class in self's MRO (C), not strictly B's declaration parent A.")],
      "It returns ['D', 'B', 'C', 'A']. Python's super() follows the instance's Method Resolution Order "
      "(D.__mro__ is D, B, C, A, object). Inside B.ping, super().ping() calls the next class in D's MRO, which is C, "
      "and C's super().ping() then calls A—so every class in the diamond runs once."),

    FB(D, "advanced", PY, "Missing code: mark an abstract method in Python",
       """from abc import ABC, abstractmethod

class Serializer(ABC):
    ____
    def dumps(self, data: dict) -> str:
        pass""",
       "Fill in the decorator so Serializer cannot be instantiated unless a subclass implements dumps.",
       ["@abstractmethod"],
       [("@abstractmethod on an ABC subclass prevents instantiating classes that do not override dumps", ["abstract", "instantiate", "override", "subclass", "abc"], 1)],
       [("uses @staticmethod", ["@staticmethod"], "@staticmethod does not enforce overriding in subclasses.")],
       "The decorator is @abstractmethod. Together with inheriting from ABC, @abstractmethod prevents instantiating "
       "Serializer (or any subclass that omits dumps) with a TypeError until dumps is overridden."),

    # ── JavaScript · Beginner ───────────────────────────────────────────────
    Q(D, "beginner", JS, "Class constructor and instance methods in JS",
      """class Meter {
  constructor(start) {
    this.value = start;
  }
  advance(step) {
    this.value += step;
    return this.value;
  }
}
const m1 = new Meter(10);
const m2 = new Meter(0);
console.log(m1.advance(5), m2.advance(3));""",
      "What does this log, and what happens when new Meter(10) is evaluated?",
      [("logs 15 3", ["15 3", "15 and 3"], 2),
       ("new creates a fresh object, binds this to it, and runs constructor(10)", ["new", "this", "constructor", "instance"], 1.5),
       ("m1 and m2 have independent this.value properties", ["independent", "separate", "own"], 1)],
      [],
      "It logs 15 3. Evaluating new Meter(10) creates a fresh object linked to Meter.prototype, binds this to that "
      "instance inside constructor(10) to set m1.value = 10, and returns it. m1 and m2 hold separate value properties."),

    Q(D, "beginner", JS, "Reading a property without this in JavaScript",
      """class Rectangle {
  constructor(width, height) {
    this.width = width;
    this.height = height;
  }
  area() {
    return width * height;
  }
}
console.log(new Rectangle(4, 5).area());""",
      "What happens when area() is called, and why?",
      [("throws ReferenceError: width is not defined", ["referenceerror", "not defined", "throws", "error"], 2),
       ("JavaScript does not implicitly look up instance properties in scope; you must write this.width * this.height", ["this.width", "this.height", "scope", "implicit"], 1.5)],
      [("thinks it logs 20", ["logs 20", "prints 20", "returns 20"], "Unlike C++ or Java, JavaScript never resolves bare identifiers to properties on this.")],
      "It throws ReferenceError: width is not defined. JavaScript resolves bare identifiers like width through "
      "lexical scope, not on the object instance. Inside area(), you must write return this.width * this.height;."),

    FB(D, "beginner", JS, "Missing code: initialize an instance property on this",
       """class Todo {
  constructor(title) {
    ____;
    this.done = false;
  }
}
const t = new Todo("Ship OOP");
console.log(t.title, t.done); // Ship OOP false""",
       "Fill in the blank in constructor so t.title holds the argument passed to new Todo(...).",
       ["this.title = title"],
       [("assigns the parameter title to the instance property this.title", ["this.title", "instance", "property"], 1)],
       [("writes let title = title", ["let title"], "A local let binding disappears when constructor finishes instead of attaching a property to this.")],
       "The blank is this.title = title. Attaching title as a property on this stores it on the newly constructed "
       "Todo instance."),

    # ── JavaScript · Intermediate ───────────────────────────────────────────
    Q(D, "intermediate", JS, "Private fields with #balance",
      """class Wallet {
  #balance = 0;
  deposit(amount) {
    if (amount > 0) this.#balance += amount;
  }
  get balance() {
    return this.#balance;
  }
}
const w = new Wallet();
w.deposit(50);
console.log(w.balance);""",
      "What does this log, and what happens if code outside Wallet writes w.#balance = 9999?",
      [("logs 50", ["50", "logs 50"], 1.5),
       ("#balance is a hard-private class field; accessing w.#balance outside Wallet is a SyntaxError", ["syntaxerror", "private", "#balance", "outside"], 2),
       ("get balance() exposes a read-only getter while deposit() controls mutations", ["getter", "read-only", "encapsulat"], 1)],
      [("thinks w.#balance returns undefined outside the class", ["returns undefined"], "Touching a #private field outside its declaring class body is a compile-time SyntaxError in JavaScript.")],
      "It logs 50. #balance is a truly private class field enforced by the JS engine: accessing w.#balance outside "
      " the Wallet class body throws a SyntaxError. Callers can read the value via the get balance() getter and can "
      "only modify it through deposit()."),

    Q(D, "intermediate", JS, "Using this before super() in a subclass constructor",
      """class Animal {
  constructor(name) {
    this.name = name;
  }
}
class Dog extends Animal {
  constructor(name, breed) {
    this.breed = breed;
    super(name);
  }
}
new Dog("Rex", "Collie");""",
      "What happens when new Dog('Rex', 'Collie') runs, and how should the constructor be ordered?",
      [("throws ReferenceError because this is used before super(name)", ["referenceerror", "before super", "must call super"], 2),
       ("in a derived JS class, super(...) initializes the this binding, so super(name) must come before this.breed = breed", ["super(name)", "derived", "initializ", "first"], 1.5)],
      [],
      "It throws a ReferenceError (Must call super constructor in derived class before accessing 'this'). In "
      "JavaScript subclasses (extends), the parent constructor allocates/initializes the this binding, so super(name) "
      "must be called before any reference to this.breed."),

    FB(D, "intermediate", JS, "Missing code: inherit from a base class in JavaScript",
       """class Shape {
  describe() { return "shape"; }
}
class Circle ____ {
  constructor(r) {
    super();
    this.r = r;
  }
}
console.log(new Circle(3).describe()); // shape""",
       "Fill in the blank in the class header so Circle inherits from Shape.",
       ["extends Shape"],
       [("extends links Circle.prototype to Shape.prototype so Circle instances inherit describe()", ["extends", "prototype", "inherit"], 1)],
       [],
       "The blank is extends Shape. The extends clause sets up prototype delegation from Circle.prototype to "
       "Shape.prototype so instances of Circle inherit describe()."),

    Q(D, "intermediate", JS, "Static factory method vs instance method",
      """class Temperature {
  constructor(celsius) {
    this.celsius = celsius;
  }
  static fromFahrenheit(f) {
    return new Temperature((f - 32) * 5 / 9);
  }
}
const t = Temperature.fromFahrenheit(212);
console.log(t.celsius);""",
      "What does this log, and what would happen if you called t.fromFahrenheit(32) on the instance t?",
      [("logs 100", ["100", "logs 100"], 1.5),
       ("t.fromFahrenheit(32) throws TypeError (t.fromFahrenheit is not a function) because static methods live on the class constructor, not on instances", ["typeerror", "not a function", "on the class", "constructor", "not on instance"], 2)],
      [],
      "It logs 100. static fromFahrenheit is attached to the Temperature constructor itself, not to "
      "Temperature.prototype, so calling t.fromFahrenheit(32) on an instance throws TypeError: t.fromFahrenheit is "
      "not a function."),

    # ── JavaScript · Advanced ───────────────────────────────────────────────
    Q(D, "advanced", JS, "Lost this when passing a method as a callback",
      """class Button {
  constructor(label) {
    this.label = label;
  }
  click() {
    return `Clicked ${this.label}`;
  }
}
const btn = new Button("Save");
const handler = btn.click;
console.log(handler());""",
      "What happens when handler() is called, why, and how do you fix it?",
      [("throws TypeError: Cannot read properties of undefined (reading 'label')", ["typeerror", "undefined", "cannot read"], 2),
       ("class methods run in strict mode and calling handler() as a plain function sets this to undefined", ["strict mode", "plain function", "unbound", "this is undefined"], 1.5),
       ("fix with btn.click.bind(btn) or () => btn.click()", ["bind", "arrow", "() =>"], 1)],
      [("thinks it logs 'Clicked Save'", ["clicked save"], "Extracting btn.click detaches the method from btn; calling handler() has this === undefined.")],
      "It throws TypeError: Cannot read properties of undefined (reading 'label'). Class bodies always execute in "
      "strict mode, and calling the extracted function handler() without a receiver sets this to undefined. Fix it "
      "with const handler = btn.click.bind(btn) or const handler = () => btn.click()."),

    Q(D, "advanced", JS, "Shared array on a prototype vs instance field",
      """function Team() {}
Team.prototype.members = [];
Team.prototype.add = function (name) {
  this.members.push(name);
};

const a = new Team();
const b = new Team();
a.add("Kai");
console.log(b.members);""",
      "What does console.log(b.members) output, why, and where should members = [] be placed?",
      [("logs ['Kai']", ["['kai']", '["kai"]', "kai"], 2),
       ("Team.prototype.members is one shared array on the prototype mutated in place by push", ["prototype", "shared", "mutat", "push"], 1.5),
       ("put this.members = [] inside the Team constructor so each instance gets its own array", ["this.members = []", "constructor", "own array"], 1)],
      [],
      "It logs ['Kai']. Because members is defined on Team.prototype, both a and b look up the exact same array on "
      "the prototype and this.members.push('Kai') mutates that shared array in place. Initialize this.members = [] "
      "inside function Team() { this.members = []; } (or a class constructor) so each instance owns a separate array."),

    Q(D, "advanced", JS, "Polymorphic dispatch vs switch on type tags",
      """class PercentageDiscount {
  constructor(pct) { this.pct = pct; }
  apply(total) { return total * (1 - this.pct); }
}
class FlatDiscount {
  constructor(off) { this.off = off; }
  apply(total) { return Math.max(0, total - this.off); }
}
function checkout(total, discounts) {
  return discounts.reduce((acc, d) => d.apply(acc), total);
}
console.log(checkout(100, [new PercentageDiscount(0.1), new FlatDiscount(15)]));""",
      "What does this log, and why is calling d.apply(acc) better design than a switch on discount.type?",
      [("logs 75 (100 -> 90 -> 75)", ["75", "logs 75"], 2),
       ("polymorphism: each discount class encapsulates its own rule behind apply(total) so new discount types can be added without modifying checkout", ["polymorph", "open/closed", "without modifying", "encapsulat", "apply"], 1.5)],
      [],
      "It logs 75 (100 * 0.9 = 90, then 90 - 15 = 75). Because every discount object exposes the same apply(total) "
      "method, checkout uses polymorphic dispatch and never needs to know which concrete discount types exist—new "
      "discount classes can be added without editing checkout."),

    FB(D, "advanced", JS, "Missing code: bind a method so this stays bound",
       """class Counter {
  constructor() {
    this.count = 0;
    this.inc = ____;
  }
  inc() {
    this.count += 1;
    return this.count;
  }
}
const c = new Counter();
const fn = c.inc;
console.log(fn()); // 1""",
       "Fill in the blank in constructor so extracting c.inc into fn still uses c as this.",
       ["this.inc.bind(this)"],
       [(".bind(this) returns a new function with this permanently bound to the Counter instance", ["bind", "permanently", "instance", "this"], 1)],
       [("writes this.inc()", ["this.inc()"], "this.inc() calls the method immediately instead of returning a bound function.")],
       "The blank is this.inc.bind(this). Function.prototype.bind returns a bound function whose this is permanently "
       "fixed to the Counter instance, even when invoked later as a bare callback fn()."),

    # ── PHP · Beginner ──────────────────────────────────────────────────────
    Q(D, "beginner", PHP, "PHP class, __construct, and $this",
      """<?php
class Book {
    public string $title;
    public int $pages;

    public function __construct(string $title, int $pages) {
        $this->title = $title;
        $this->pages = $pages;
    }

    public function summary(): string {
        return $this->title . " (" . $this->pages . "p)";
    }
}
$b = new Book("Dune", 412);
echo $b->summary();""",
      "What does this script output, and how does $this->title differ from $title inside __construct?",
      [("outputs Dune (412p)", ["dune (412p)"], 2),
       ("$this->title is the property on the Book instance, whereas $title is the constructor parameter", ["$this->title", "property", "instance", "parameter"], 1.5)],
      [],
      "It outputs Dune (412p). Inside __construct, $title is the local parameter passed into the constructor, while "
      "$this->title refers to the title property on the Book instance being constructed ($b)."),

    Q(D, "beginner", PHP, "Using $count instead of $this->count in a PHP method",
      """<?php
class Tally {
    public int $count = 0;

    public function bump(): void {
        $count = 1;
    }
}
$t = new Tally();
$t->bump();
echo $t->count;""",
      "What does this echo, why didn't $t->count change, and how do you fix bump()?",
      [("echoes 0", ["0", "echoes 0", "prints 0"], 2),
       ("$count = 1 assigns to a local variable inside bump(), not the object property $this->count", ["local variable", "$this->count", "property"], 1.5),
       ("fix: write $this->count = 1 (or $this->count++)", ["$this->count =", "$this->count++", "$this->count +="], 1)],
      [],
      "It echoes 0. In PHP, $count inside bump() is a function-local variable that disappears when bump() returns; "
      "object properties must always be accessed through $this->count; fix it by writing $this->count = 1."),

    FB(D, "beginner", PHP, "Missing code: read an instance property via $this",
       """<?php
class User {
    public string $handle;
    public function __construct(string $handle) {
        $this->handle = $handle;
    }
    public function tag(): string {
        return "@" . ____;
    }
}
echo (new User("ada"))->tag(); // @ada""",
       "Fill in the blank so tag() returns '@' followed by the instance's handle property.",
       ["$this->handle"],
       [("$this->handle reads the handle property on the current User instance", ["$this->handle", "property", "instance"], 1)],
       [("writes $this->$handle", ["$this->$handle"], "$this->$handle is a variable property lookup; the property name is handle, so write $this->handle.")],
       "The blank is $this->handle. In PHP, instance properties are accessed with the -> operator on $this (without "
       "a second $ before the property name)."),

    # ── PHP · Intermediate ──────────────────────────────────────────────────
    Q(D, "intermediate", PHP, "private vs protected visibility in a PHP subclass",
      """<?php
class Vault {
    private int $pin = 1234;
    protected int $balance = 500;
}
class SavingsVault extends Vault {
    public function report(): int {
        return $this->balance;
    }
}
echo (new SavingsVault())->report();""",
      "What does this output, and what would happen if report() returned $this->pin instead?",
      [("outputs 500", ["500", "outputs 500"], 1.5),
       ("protected members ($balance) are accessible in subclasses, whereas private members ($pin) are visible only inside Vault itself", ["protected", "private", "subclass", "child", "only inside vault"], 2)],
      [],
      "It outputs 500. $balance is declared protected, so Vault and its subclass SavingsVault can access it via "
      "$this->balance. $pin is private to Vault alone, so reading $this->pin inside SavingsVault would fail with "
      "an undefined/private property error."),

    Q(D, "intermediate", PHP, "Calling parent::__construct in PHP",
      """<?php
class Employee {
    public string $name;
    public function __construct(string $name) {
        $this->name = $name;
    }
}
class Manager extends Employee {
    public int $teamSize;
    public function __construct(string $name, int $teamSize) {
        parent::__construct($name);
        $this->teamSize = $teamSize;
    }
}
$m = new Manager("Rosa", 6);
echo $m->name . ":" . $m->teamSize;""",
      "What does this output, and what happens in PHP if a child defines __construct without calling parent::__construct?",
      [("outputs Rosa:6", ["rosa:6"], 2),
       ("PHP does not automatically call the parent constructor when the child defines __construct, so $this->name would remain uninitialized without parent::__construct($name)", ["not automatic", "parent::__construct", "uninitialized", "explicitly"], 1.5)],
      [],
      "It outputs Rosa:6. When a PHP subclass defines its own __construct, PHP does not implicitly call the parent "
      "constructor; without parent::__construct($name), Employee::__construct would never run and $m->name would "
      "remain uninitialized."),

    FB(D, "intermediate", PHP, "Missing code: invoke the parent constructor in PHP",
       """<?php
class BaseJob {
    public int $retries;
    public function __construct(int $retries) {
        $this->retries = $retries;
    }
}
class EmailJob extends BaseJob {
    public string $to;
    public function __construct(int $retries, string $to) {
        ____;
        $this->to = $to;
    }
}""",
       "Fill in the blank so EmailJob runs BaseJob's constructor with $retries.",
       ["parent::__construct($retries)"],
       [("parent::__construct($retries) calls the immediate base class constructor on the current instance", ["parent::__construct", "base", "parent", "constructor"], 1)],
       [("writes super($retries)", ["super($retries)"], "PHP uses parent::__construct(...), not super(...).")],
       "The blank is parent::__construct($retries). PHP uses the parent:: scope resolution operator to invoke the "
       "overridden constructor in BaseJob."),

    Q(D, "intermediate", PHP, "Static property self::$count vs instance property",
      """<?php
class Ticket {
    public static int $issued = 0;
    public int $number;

    public function __construct() {
        self::$issued++;
        $this->number = self::$issued;
    }
}
$a = new Ticket();
$b = new Ticket();
echo $a->number . "," . $b->number . "," . Ticket::$issued;""",
      "What does this echo, and why do we use self::$issued instead of $this->issued?",
      [("echoes 1,2,2", ["1,2,2"], 2),
       ("self::$issued belongs to the Ticket class as a whole so it persists across all instances, while $this->number belongs to each individual Ticket", ["static", "class", "shared", "each instance", "$this->number"], 1.5)],
      [],
      "It echoes 1,2,2. Static property Ticket::$issued (accessed via self::$issued) belongs to the class itself and "
      "is shared across every constructor call, incrementing from 0 to 1 to 2, while $this->number stores each "
      "ticket's own serial number on that instance."),

    # ── PHP · Advanced ──────────────────────────────────────────────────────
    Q(D, "advanced", PHP, "PHP interface contract and polymorphic type hinting",
      """<?php
interface Mailer {
    public function send(string $to, string $body): bool;
}
class SmtpMailer implements Mailer {
    public function send(string $to, string $body): bool { return true; }
}
class FakeMailer implements Mailer {
    public array $sent = [];
    public function send(string $to, string $body): bool {
        $this->sent[] = $to;
        return true;
    }
}
function welcome(Mailer $mailer, string $email): void {
    $mailer->send($email, "Welcome!");
}""",
      "Why is typing welcome(Mailer $mailer, ...) against the interface better than typing welcome(SmtpMailer $mailer, ...)?",
      [("decouples welcome() from concrete transport so any class implementing Mailer (like FakeMailer in tests) can be passed", ["decoupl", "fake", "test", "any class", "implements", "polymorph"], 2),
       ("the interface guarantees send(string $to, string $body): bool exists on any passed object", ["contract", "guarantee", "send("], 1.5)],
      [],
      "Typing against the Mailer interface decouples welcome() from SmtpMailer: production code can pass SmtpMailer "
      "while unit tests pass FakeMailer (dependency injection) without sending real emails, and PHP enforces at "
      "call time that any implementation provides send(string $to, string $body): bool."),

    Q(D, "advanced", PHP, "Late static binding in PHP: self:: vs static::",
      """<?php
class Model {
    public static function table(): string { return "models"; }
    public static function queryUsingSelf(): string { return "SELECT * FROM " . self::table(); }
    public static function queryUsingStatic(): string { return "SELECT * FROM " . static::table(); }
}
class Invoice extends Model {
    public static function table(): string { return "invoices"; }
}
echo Invoice::queryUsingSelf() . " | " . Invoice::queryUsingStatic();""",
      "What does this echo, and why do self::table() and static::table() differ when called via Invoice?",
      [("echoes SELECT * FROM models | SELECT * FROM invoices", ["select * from models | select * from invoices", "models", "invoices"], 2),
       ("self:: resolves at compile time to the class where the method is defined (Model), while static:: uses late static binding to resolve to the runtime called class (Invoice)", ["late static binding", "compile", "runtime", "called class", "defining class"], 1.5)],
      [],
      "It echoes SELECT * FROM models | SELECT * FROM invoices. self::table() binds early to Model (the class where "
      "queryUsingSelf is defined), whereas static::table() uses late static binding and resolves to Invoice, the "
      "class on which the static call was actually made at runtime."),

    FB(D, "advanced", PHP, "Missing code: implement an interface in PHP",
       """<?php
interface CacheStore {
    public function get(string $key): ?string;
}
class MemoryCache ____ {
    private array $data = [];
    public function get(string $key): ?string {
        return $this->data[$key] ?? null;
    }
}""",
       "Fill in the blank in the class declaration so MemoryCache fulfills the CacheStore interface.",
       ["implements CacheStore"],
       [("implements declares that MemoryCache provides every method in CacheStore", ["implements", "interface", "contract"], 1)],
       [("uses extends CacheStore", ["extends CacheStore"], "In PHP, a class uses implements for an interface and extends for a class.")],
       "The blank is implements CacheStore. A PHP class uses the implements keyword to declare that it satisfies "
       "an interface contract."),

    # ── C++ · Beginner ──────────────────────────────────────────────────────
    Q(D, "beginner", CPP, "Class encapsulation and public methods in C++",
      """#include <iostream>

class Counter {
    int value_ = 0;
public:
    void add(int n) { value_ += n; }
    int get() const { return value_; }
};

int main() {
    Counter c;
    c.add(4);
    c.add(3);
    std::cout << c.get() << "\\n";
}""",
      "What does this print, why is value_ private even without the keyword private:, and what does const on get() mean?",
      [("prints 7", ["7", "prints 7"], 1.5),
       ("members of a C++ class are private by default before the first access specifier", ["private by default", "default access", "private"], 1.5),
       ("get() const promises not to modify the Counter object and allows calling get() on const Counter references", ["does not modify", "not mutate", "const counter", "const object", "const reference", "read-only"], 1)],
      [],
      "It prints 7. In a C++ class (unlike struct), members declared before the first access specifier are private "
      "by default, so value_ can only be modified through add(). Marking get() const guarantees it does not mutate "
      "member variables and lets callers invoke c.get() on a const Counter."),

    Q(D, "beginner", CPP, "Member initializer list for const and reference members",
      """#include <iostream>

class Tag {
    const int id_;
public:
    Tag(int id) : id_(id) {}
    int id() const { return id_; }
};

int main() {
    Tag t(42);
    std::cout << t.id() << "\\n";
}""",
      "Why must id_ be initialized with : id_(id) in the member initializer list instead of id_ = id; inside the constructor body?",
      [("const (and reference) data members must be initialized when constructed, before the constructor body begins", ["const", "before the body", "initializer list", "cannot be assigned"], 2),
       ("writing id_ = id inside the body is assignment to an already-constructed const member, which fails to compile", ["assign", "compile", "already constructed"], 1.5)],
      [],
      "In C++, all data members are initialized before the constructor body `{ ... }` executes. A const member (or "
      "reference member) cannot be default-constructed and assigned later inside the body, so it must be initialized "
      "directly in the member initializer list `: id_(id)`."),

    FB(D, "beginner", CPP, "Missing code: initialize a member in a C++ constructor",
       """#include <iostream>

class Box {
    int width_;
public:
    Box(int w) : ____ {}
    int width() const { return width_; }
};

int main() {
    std::cout << Box(9).width() << "\\n"; // 9
}""",
       "Fill in the member initializer list so width_ is initialized with w.",
       ["width_(w)", "width_{w}"],
       [("width_(w) initializes the member width_ directly from parameter w before the constructor body runs", ["initializer list", "width_", "direct", "before"], 1)],
       [],
       "The blank is width_(w) (or width_{w}). In a C++ constructor's member initializer list after `:`, `width_(w)` "
       "initializes the data member `width_` with `w`."),

    # ── C++ · Intermediate ──────────────────────────────────────────────────
    Q(D, "intermediate", CPP, "Polymorphic dispatch with virtual and override",
      """#include <iostream>
#include <string>

struct Animal {
    virtual std::string speak() const { return "..."; }
    virtual ~Animal() = default;
};
struct Dog : Animal {
    std::string speak() const override { return "woof"; }
};

void greet(const Animal& a) {
    std::cout << a.speak() << "\\n";
}

int main() {
    Dog d;
    greet(d);
}""",
      "What does this print, and why are both virtual on Animal::speak and passing const Animal& by reference required?",
      [("prints woof", ["woof", "prints woof"], 1.5),
       ("virtual enables dynamic dispatch (vtable lookup) based on the runtime type Dog, and const Animal& avoids slicing the Dog down to an Animal", ["virtual", "dynamic dispatch", "runtime type", "reference", "slicing"], 2),
       ("override lets the compiler verify the signature matches a base virtual function", ["override", "compiler", "signature"], 0.5)],
      [],
      "It prints woof. Because Animal::speak is declared virtual and greet takes `const Animal&` by reference, "
      "calling a.speak() dispatches dynamically at runtime to Dog::speak(). Passing by reference preserves the "
      "actual Dog object, and `override` asks the compiler to verify that Dog::speak matches the base signature."),

    Q(D, "intermediate", CPP, "Non-virtual method call on a base reference",
      """#include <iostream>

struct Shape {
    int sides() const { return 0; }
};
struct Triangle : Shape {
    int sides() const { return 3; }
};

void show(const Shape& s) {
    std::cout << s.sides() << "\\n";
}

int main() {
    Triangle t;
    show(t);
}""",
      "What does show(t) print, why doesn't it call Triangle::sides(), and how do you fix it?",
      [("prints 0", ["prints 0", "0"], 2),
       ("Shape::sides() is not virtual, so s.sides() is bound statically at compile time using the static type const Shape&", ["not virtual", "non-virtual", "static", "compile time", "shape::sides"], 1.5),
       ("fix: mark int sides() const as virtual in Shape (and override in Triangle)", ["virtual", "override"], 1)],
      [("thinks it prints 3 because s is passed by reference", ["prints 3"], "A reference alone does not trigger dynamic dispatch in C++; the base method must also be declared virtual.")],
      "It prints 0. Because Shape::sides() is not declared virtual, C++ resolves s.sides() at compile time using the "
      "parameter's static type (`const Shape&`), calling Shape::sides(). Add `virtual` to Shape::sides() (and "
      "`override` in Triangle) to get runtime dispatch."),

    FB(D, "intermediate", CPP, "Missing code: enable dynamic dispatch on a C++ base method",
       """#include <iostream>

struct Instrument {
    ____ int pitch() const { return 440; }
    virtual ~Instrument() = default;
};
struct TuningFork : Instrument {
    int pitch() const override { return 528; }
};

int main() {
    TuningFork f;
    const Instrument& ref = f;
    std::cout << ref.pitch() << "\\n"; // 528
}""",
       "Fill in the keyword on Instrument::pitch so calling ref.pitch() dispatches to TuningFork::pitch.",
       ["virtual"],
       [("virtual enables runtime polymorphic dispatch through a base reference or pointer", ["virtual", "runtime", "dynamic dispatch", "override"], 1)],
       [],
       "The blank is virtual. Declaring the base method `virtual` enables dynamic dispatch when called through a "
       "`const Instrument&` reference or `Instrument*` pointer."),

    Q(D, "intermediate", CPP, "Static data member shared across C++ instances",
      """#include <iostream>

class Session {
public:
    inline static int active = 0;
    Session() { ++active; }
    ~Session() { --active; }
};

int main() {
    Session a;
    {
        Session b;
        std::cout << Session::active << " ";
    }
    std::cout << a.active << "\\n";
}""",
      "What does this print, and why does Session::active decrease when the inner block ends?",
      [("prints 2 1", ["2 1", "2 and 1"], 2),
       ("active is a static member shared by the whole Session class, incremented in the constructor and decremented when b's destructor runs at the end of the inner scope", ["static", "shared", "destructor", "scope", "b goes out of scope"], 1.5)],
      [],
      "It prints 2 1. `active` is a single static variable shared by the Session class. Constructing `a` and `b` "
      "increments `active` to 2; when the inner `{ ... }` block exits, `b` goes out of scope and its destructor "
      "`~Session()` runs automatically, decrementing `active` back to 1."),

    # ── C++ · Advanced ──────────────────────────────────────────────────────
    Q(D, "advanced", CPP, "Object slicing when passing a derived object by value",
      """#include <iostream>
#include <string>

struct Base {
    virtual std::string name() const { return "Base"; }
    virtual ~Base() = default;
};
struct Derived : Base {
    int extra = 99;
    std::string name() const override { return "Derived"; }
};

void printName(Base b) {
    std::cout << b.name() << "\\n";
}

int main() {
    Derived d;
    printName(d);
}""",
      "What does printName(d) print, what happened to the Derived part of d, and how should printName take its parameter?",
      [("prints Base", ["prints base", "base"], 2),
       ("object slicing: passing Base b by value copy-constructs a brand-new Base subobject, slicing off extra and Derived's vptr", ["slic", "by value", "copy", "base subobject", "vptr"], 1.5),
       ("fix: pass by const reference (const Base& b)", ["const base&", "by reference"], 1)],
      [("thinks virtual makes it print Derived even by value", ["prints derived"], "virtual only dispatches dynamically through a pointer or reference; passing by value constructs a plain Base object.")],
      "It prints Base. Because printName takes `Base b` by value, passing `d` invokes `Base`'s copy constructor to "
      "create a standalone `Base` object—slicing off `Derived::extra` and setting `b`'s vptr to `Base`. Fix it by "
      "taking `const Base& b` by reference."),

    Q(D, "advanced", CPP, "Deleting a derived object through a base pointer without a virtual destructor",
      """struct Base {
    ~Base() {}
};
struct Derived : Base {
    int* buf;
    Derived() : buf(new int[100]) {}
    ~Derived() { delete[] buf; }
};

int main() {
    Base* p = new Derived();
    delete p;
}""",
      "What bug occurs on delete p, and how do you fix Base (and Derived)?",
      [("undefined behaviour and ~Derived() is not called (leaking buf) because Base's destructor is not virtual", ["undefined behavior", "undefined behaviour", "virtual destructor", "~derived", "leak"], 2),
       ("fix: declare virtual ~Base() = default; (and prefer std::vector<int> or std::unique_ptr for RAII)", ["virtual ~base", "unique_ptr", "vector", "raii"], 1.5)],
      [],
      "Deleting a `Derived` object through a `Base*` pointer when `~Base()` is not `virtual` is undefined behaviour "
      "in C++ (and in practice skips `~Derived()`, leaking `buf`). Fix `Base` by declaring `virtual ~Base() = default;` "
      "(and use `std::vector<int>` or `std::unique_ptr<int[]>` inside `Derived` for RAII)."),

    FB(D, "advanced", CPP, "Missing code: declare a pure virtual function in C++",
       """struct Shape {
    virtual double area() const ____;
    virtual ~Shape() = default;
};""",
       "Fill in the blank so area() is a pure virtual function and Shape is an abstract class.",
       ["= 0"],
       [("= 0 makes area() a pure virtual function so Shape cannot be instantiated directly and concrete subclasses must override it", ["pure virtual", "abstract", "instantiate", "override"], 1)],
       [],
       "The blank is = 0. Writing `= 0` at the end of a virtual function declaration makes it a pure virtual "
       "function, turning `Shape` into an abstract class that cannot be instantiated directly."),

    # ── General · Beginner ──────────────────────────────────────────────────
    Q(D, "beginner", GEN, "Class vs instance: blueprint vs house",
      """Class:    BankAccount(owner, balance)
Objects:  acct1 = BankAccount("Ana", 500)
          acct2 = BankAccount("Ben", 120)

acct1.withdraw(100)""",
      "Explain the difference between the BankAccount class and the objects acct1 and acct2, and state both balances after acct1.withdraw(100).",
      [("acct1 has 400 and acct2 still has 120", ["400", "120"], 2),
       ("a class is the blueprint/template defining structure and methods, while each instance/object holds its own independent state in memory", ["blueprint", "template", "instance", "own state", "independent", "separate"], 1.5)],
      [],
      "After acct1.withdraw(100), acct1's balance is 400 and acct2's balance is still 120. The class BankAccount is "
      "the blueprint that defines what attributes (owner, balance) and methods (withdraw) an account has, while "
      "acct1 and acct2 are two separate instances in memory, each holding its own state."),

    Q(D, "beginner", GEN, "Bundling state and behaviour together",
      """Design A (globals / loose data):
  door_locked = True
  door_open = False
  # any function anywhere can set door_open = True while door_locked is True

Design B (Door object):
  door.open()   # checks if self.locked first; refuses if locked""",
      "What problem does Design B solve that Design A cannot prevent?",
      [("prevents invalid state (an open door that is still locked) by routing state changes through methods that enforce rules", ["invalid", "inconsistent", "invariant", "locked", "enforce", "encapsulat"], 2),
       ("in Design A any caller can mutate loose variables directly and forget the check", ["any caller", "forget", "directly", "scattered"], 1)],
      [],
      "Design B prevents inconsistent state (a door that is simultaneously locked and open). In Design A, any piece "
      "of code can set door_open = True directly and forget to check door_locked. By bundling state with the methods "
      "that modify it, the Door object enforces the rule in one place."),

    # ── General · Intermediate ──────────────────────────────────────────────
    Q(D, "intermediate", GEN, "Encapsulation: why hide internal representation?",
      """Version 1 of Temperature stores degrees Celsius in a private field.
Version 2 changes internal storage to Kelvin, while keeping getCelsius() and setCelsius(c) unchanged.""",
      "Why does making the storage field private (instead of public) make the change from Version 1 to Version 2 safe for callers?",
      [("callers depend only on the public methods getCelsius/setCelsius, so changing the private field from Celsius to Kelvin does not break any caller code", ["caller", "public method", "without breaking", "internal representation", "decoupl", "interface"], 2),
       ("if the field were public, every caller reading or writing it directly would break or miscalculate when the unit changed", ["directly", "public field", "break", "every caller"], 1)],
      [],
      "Because the internal field is private, outside code only interacts with Temperature through its public "
      "contract (getCelsius() and setCelsius(c)). Version 2 can convert to and from Kelvin inside those two methods "
      "without breaking a single caller, whereas a public field would force every caller in the codebase to be rewritten."),

    Q(D, "intermediate", GEN, "Is-a (inheritance) vs has-a (composition)",
      """Design A:  class Car extends Engine { ... }
Design B:  class Car { private Engine engine; ... }""",
      "Which design is better and why? Use the 'is-a' vs 'has-a' rule and explain what happens if you want to swap in an ElectricMotor.",
      [("Design B (composition) is better because a Car has an Engine, it is not a kind of Engine", ["design b", "has-a", "has an", "composition", "not an engine"], 2),
       ("with composition Car can hold any Engine/Motor interface and swap ElectricMotor without changing Car's class hierarchy, whereas inheritance exposes all Engine internals on Car", ["swap", "electric", "interface", "tightly coupled", "expose"], 1.5)],
      [("picks Design A because it writes less code", ["design a is better"], "Inheritance models 'is-a'; a Car is not an Engine, and extending Engine couples Car to one concrete engine implementation.")],
      "Design B (composition) is better. A Car *has an* Engine ('has-a'), it is not a subtype of Engine ('is-a'). "
      "With composition, Car delegates only what it needs to its engine field and can swap a GasEngine for an "
      "ElectricMotor behind a common interface without changing Car's hierarchy or leaking Engine methods onto Car."),

    # ── General · Advanced ──────────────────────────────────────────────────
    Q(D, "advanced", GEN, "Composition over inheritance: the class explosion problem",
      """Hierarchy using inheritance alone:
  Notifier
  ├── EmailTextNotifier
  ├── EmailHtmlNotifier
  ├── SmsTextNotifier
  ├── SmsHtmlNotifier
  ├── SlackTextNotifier
  └── SlackHtmlNotifier
(Now the team wants to add Push notifications and Markdown formatting.)""",
      "How many subclasses are needed with inheritance for M transports and N formats, and how does composition solve this?",
      [("inheritance requires M * N subclasses (adding 1 transport + 1 format grows 3x2=6 to 4x3=12 classes)", ["m * n", "m x n", "12", "combinatorial", "explosion", "multiply"], 2),
       ("composition separates Transport (M classes) and Formatter (N classes) so a Notifier holds one of each (M + N classes total)", ["m + n", "composition", "inject", "strategy", "separate"], 1.5)],
      [],
      "With inheritance, combining M transports with N formats requires M × N subclasses (going from 3×2 = 6 to "
      "4×3 = 12 classes). With composition, you define M Transport classes and N Formatter classes (4 + 3 = 7 total) "
      "and give Notifier a Transport reference and a Formatter reference that can be combined freely at runtime."),

    Q(D, "advanced", GEN, "Liskov Substitution Principle: Square extending Rectangle",
      """class Rectangle:
    setWidth(w)
    setHeight(h)
    area() -> width * height

class Square extends Rectangle:
    setWidth(w)  -> sets BOTH width and height to w
    setHeight(h) -> sets BOTH width and height to h

def resize_and_check(rect: Rectangle):
    rect.setWidth(5)
    rect.setHeight(4)
    assert rect.area() == 20""",
      "What happens when a Square is passed to resize_and_check, and which OOP principle does Square extends Rectangle violate?",
      [("assertion fails because rect.area() is 16 (setHeight(4) overwrote width to 4), not 20", ["16", "fails", "overwrote", "both width and height"], 2),
       ("violates the Liskov Substitution Principle (LSP): a subclass must honour the behavioural contract of its base class (setting height on a Rectangle must not change width)", ["liskov", "lsp", "substitut", "contract", "postcondition", "immutable"], 1.5)],
      [],
      "The assertion fails: calling rect.setHeight(4) on a Square changes both width and height to 4, so rect.area() "
      "is 16 instead of 20. This violates the Liskov Substitution Principle (LSP): a mutable Square cannot be "
      "substituted where a mutable Rectangle is expected because Rectangle's contract assumes width and height vary "
      "independently. Make both classes immutable shapes implementing a Shape.area() interface instead."),

    # ── Java · Beginner ─────────────────────────────────────────────────────
    Q(D, "beginner", JAVA, "Java class, constructor, and separate instances",
      """class Counter {
    private int count;

    public Counter(int start) {
        this.count = start;
    }
    public void increment() {
        this.count++;
    }
    public int getCount() {
        return this.count;
    }
}
Counter a = new Counter(10);
Counter b = new Counter(0);
a.increment();
System.out.println(a.getCount() + " " + b.getCount());""",
      "What does this print, and why doesn't a.increment() change b.getCount()?",
      [("prints 11 0", ["11 0", "11 and 0"], 2),
       ("each new Counter(...) allocates a separate object in memory with its own instance field count", ["separate", "own", "instance", "two objects", "independent"], 1.5)],
      [],
      "It prints 11 0. Each `new Counter(...)` call allocates an independent `Counter` instance on the heap and "
      "initializes its own `this.count` field (`10` for `a`, `0` for `b`), so `a.increment()` only increments `a.count`."),

    Q(D, "beginner", JAVA, "Parameter shadowing a field without this in Java",
      """class User {
    private String name;

    public User(String name) {
        name = name;
    }
    public String getName() {
        return this.name;
    }
}
System.out.println(new User("Ada").getName());""",
      "What does this print, why, and how do you fix the constructor?",
      [("prints null", ["null", "prints null"], 2),
       ("the parameter name shadows the field name, so name = name assigns the parameter to itself and leaves this.name at its default value null", ["shadow", "itself", "parameter", "this.name"], 1.5),
       ("fix: write this.name = name;", ["this.name = name"], 1)],
      [("thinks it prints Ada", ["prints ada"], "Without this., bare name inside User(String name) refers to the parameter, leaving the instance field this.name as null.")],
      "It prints null. Inside `User(String name)`, the parameter `name` shadows the field `name`, so `name = name;` "
      "assigns the parameter to itself and leaves the instance field `this.name` at its default value (`null`). Fix "
      "it by writing `this.name = name;`."),

    FB(D, "beginner", JAVA, "Missing code: assign the constructor parameter to the Java field",
       """class BankAccount {
    private int balance;

    public BankAccount(int balance) {
        ____;
    }
    public int getBalance() { return this.balance; }
}""",
       "Fill in the constructor body so the field balance is initialized with the parameter balance.",
       ["this.balance = balance"],
       [("this.balance refers to the instance field while bare balance is the constructor parameter", ["this.balance", "instance field", "parameter", "shadow"], 1)],
       [("writes balance = balance", ["balance = balance"], "balance = balance assigns the parameter to itself and leaves the field this.balance as 0.")],
       "The blank is this.balance = balance. Qualifying with `this.` disambiguates the instance field `this.balance` "
       "from the constructor parameter `balance`."),

    # ── Java · Intermediate ─────────────────────────────────────────────────
    Q(D, "intermediate", JAVA, "Encapsulation with private fields and a validating setter in Java",
      """public class Wallet {
    private int cents;

    public int getCents() { return cents; }

    public void deposit(int amount) {
        if (amount <= 0) {
            throw new IllegalArgumentException("amount must be positive");
        }
        this.cents += amount;
    }
}""",
      "How does making cents private and exposing deposit(int) protect Wallet's invariant?",
      [("external code cannot set cents to a negative value directly (w.cents = -50 fails to compile), and deposit rejects non-positive amounts", ["private", "negative", "compile", "deposit", "invariant", "encapsulat"], 2),
       ("getCents() provides read access while deposit(int) enforces validation on every state change", ["getcents", "read", "state change", "enforces"], 1)],
      [],
      "Declaring `cents` as `private` prevents outside classes from writing `w.cents = -50` directly (a compile-time "
      "error). Every state change must go through `deposit(int)`, which enforces `amount > 0` and guarantees `cents` "
      "can never become negative."),

    Q(D, "intermediate", JAVA, "Inheritance with extends and super(...) in Java",
      """class Employee {
    protected final String name;
    public Employee(String name) { this.name = name; }
    public int pay() { return 1000; }
}
class Manager extends Employee {
    private final int bonus;
    public Manager(String name, int bonus) {
        super(name);
        this.bonus = bonus;
    }
    @Override
    public int pay() { return super.pay() + bonus; }
}
System.out.println(new Manager("Lin", 300).pay());""",
      "What does this print, and what two roles does super play in Manager?",
      [("prints 1300", ["1300", "prints 1300"], 2),
       ("super(name) must be the first statement in Manager's constructor to initialize Employee.name, and super.pay() calls Employee's overridden pay() method (1000) before adding bonus (300)", ["super(name)", "first statement", "super.pay()", "employee"], 1.5)],
      [],
      "It prints 1300. Inside `Manager`'s constructor, `super(name)` runs first to invoke `Employee(String)` and "
      "initialize `this.name`. Inside the overridden `pay()` method, `super.pay()` calls `Employee.pay()` (`1000`) "
      "and adds `bonus` (`300`)."),

    FB(D, "intermediate", JAVA, "Missing code: call the superclass constructor in Java",
       """class Vehicle {
    protected final String brand;
    public Vehicle(String brand) {
        this.brand = brand;
    }
}
class Truck extends Vehicle {
    private final int payloadKg;
    public Truck(String brand, int payloadKg) {
        ____;
        this.payloadKg = payloadKg;
    }
}""",
       "Fill in the first statement of Truck's constructor so Vehicle initializes brand.",
       ["super(brand)"],
       [("super(brand) invokes the superclass constructor Vehicle(String) and must be the first statement in the subclass constructor", ["super(brand)", "superclass", "parent", "first statement"], 1)],
       [],
       "The blank is super(brand). Because `Vehicle` has no no-arg constructor, `Truck` must explicitly call "
       "`super(brand)` as the first statement of its constructor."),

    Q(D, "intermediate", JAVA, "Static field vs instance field in a Java class",
      """class Session {
    private static int total = 0;
    private final int id;

    public Session() {
        total++;
        this.id = total;
    }
    public int getId() { return id; }
    public static int getTotal() { return total; }
}
Session s1 = new Session();
Session s2 = new Session();
System.out.println(s1.getId() + " " + s2.getId() + " " + Session.getTotal());""",
      "What does this print, and why is total declared static while id is an instance field?",
      [("prints 1 2 2", ["1 2 2"], 2),
       ("static total belongs to the Session class itself and is shared across all instances, while id is a per-instance field so s1 keeps 1 and s2 gets 2", ["static", "shared", "class", "per-instance", "instance field"], 1.5)],
      [],
      "It prints 1 2 2. `total` is a `static` field shared by the `Session` class as a whole, so constructing `s1` "
      "and `s2` increments `total` from 0 to 1 to 2. `id` is an instance field on each `Session` object, so `s1.id` "
      "stays 1 while `s2.id` is 2."),

    # ── Java · Advanced ─────────────────────────────────────────────────────
    Q(D, "advanced", JAVA, "Polymorphism and @Override dispatch in Java",
      """interface Shape {
    int area();
}
class Rect implements Shape {
    private final int w, h;
    Rect(int w, int h) { this.w = w; this.h = h; }
    @Override public int area() { return w * h; }
}
class Square implements Shape {
    private final int s;
    Square(int s) { this.s = s; }
    @Override public int area() { return s * s; }
}
List<Shape> shapes = List.of(new Rect(3, 4), new Square(5));
int sum = 0;
for (Shape sh : shapes) sum += sh.area();
System.out.println(sum);""",
      "What does this print, how does Java choose which area() method to run, and why is @Override valuable?",
      [("prints 37 (12 + 25)", ["37", "prints 37"], 2),
       ("Java uses dynamic (virtual) method dispatch at runtime based on each object's actual class (Rect vs Square), not the variable type Shape", ["dynamic", "runtime", "actual class", "polymorph"], 1.5),
       ("@Override makes the compiler fail if the method signature does not match a supertype method (catching typos or accidental overloading)", ["@override", "compiler", "signature", "typo"], 1)],
      [],
      "It prints 37 (`3 * 4 = 12` plus `5 * 5 = 25`). In Java, all non-static, non-private, non-final instance "
      "methods use dynamic dispatch at runtime based on the actual object (`Rect` or `Square`), even when referenced "
      "through `Shape`. Adding `@Override` instructs the compiler to verify that the method actually overrides/implements "
      "a supertype method."),

    Q(D, "advanced", JAVA, "Java interface vs abstract class",
      """interface Auditable {
    String auditLine();
}
abstract class Payment {
    protected final int cents;
    protected Payment(int cents) { this.cents = cents; }
    public abstract boolean charge();
}""",
      "When should you use a Java interface vs an abstract class, and can a single class use both?",
      [("a class can implement multiple interfaces (class CardPayment extends Payment implements Auditable, Serializable) but can extend only one class", ["multiple interfaces", "single inheritance", "only one class", "extends", "implements"], 2),
       ("abstract classes can hold non-static instance fields (like cents) and constructors for shared state, whereas interfaces define a capability contract without instance fields", ["instance field", "constructor", "state", "contract", "capability"], 1.5)],
      [],
      "Use an `interface` to define a capability contract (`Auditable`) that unrelated classes can implement—a Java "
      "class can `implements` any number of interfaces. Use an `abstract class` (`Payment`) when closely related "
      "subclasses need to share non-static instance fields (`cents`) and constructor initialization, since a class "
      "can `extends` only one superclass. A class can do both: `class CardPayment extends Payment implements Auditable`."),

    FB(D, "advanced", JAVA, "Missing code: implement a Java interface",
       """interface Notifier {
    void send(String message);
}
public class EmailNotifier ____ {
    @Override
    public void send(String message) {
        System.out.println("Email: " + message);
    }
}""",
       "Fill in the blank in the class declaration so EmailNotifier fulfills the Notifier interface.",
       ["implements Notifier"],
       [("Java uses implements (not extends) when a class adopts an interface contract", ["implements", "interface", "contract"], 1)],
       [("writes extends Notifier", ["extends Notifier"], "In Java, a class uses implements for an interface and extends for a class.")],
       "The blank is implements Notifier. In Java, a class declares that it satisfies an interface using the "
       "`implements` keyword."),
]
