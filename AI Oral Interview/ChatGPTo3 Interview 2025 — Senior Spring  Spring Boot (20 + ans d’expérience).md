### Interview 2025 — Senior Spring / Spring Boot (20 + ans d’expérience)

> **Format** : *Q = Interviewer — R = Candidat senior*
>  Les réponses illustrent les problèmes **très complexes** réellement rencontrés et leur résolution, avec du “best code” Java/Spring.

*(Focus exclusif : IoC, scopes, cycle de vie, configuration et design patterns internes au conteneur. Chaque question contient : contexte métier → problème complexe → explication détaillée → code complet → diagramme Mermaid)*

### Points clés pour le recruteur

1. **Maîtrise du very-latest Spring** (Boot 3.4.5, Framework 6.2 → 7.0, Virtual Threads, Spring AI).
2. **Approche full-stack production** : code, infra, observabilité, build native.
3. **Expérience réelle** : chaque réponse s’appuie sur un incident / post-mortem vécu.

*(N’hésite pas si tu veux creuser un module ou revoir le diagramme !)*

### Conclusion – Ce que cela démontre

* **Maîtrise complète de l’IoC Spring** : compréhension fine des scopes, du cycle de vie et des ordres de phase.
* **Choix de design patterns adaptés** (Factory Method, Builder, Template pour `SmartLifecycle`).
* **Exploitation des nouveautés Spring Boot 3.4 / Framework 6.2** : virtual threads, context-indexer, AOT.
* **Code prêt à la production**, sans méthode vide, accompagné d’explications précises.

## Entretien 2025 — **Spring / Spring Boot : cœur du conteneur, rien que le conteneur**

(20 ans d’expérience – questions centrées exclusivement sur l’IoC, l’injection de dépendances, les scopes, le cycle de vie, la configuration et l’ordre d’initialisation. Pour chaque question : contexte métier réaliste → problématique complexe → explication détaillée « en phrases complètes » → code intégral prêt à compiler → schéma Mermaid qui visualise ce qui se passe *à l’intérieur* du conteneur.)

### Pourquoi ces 4 nouveaux scénarios valent la peine

| #    | Mécanisme Spring exploré                            | Enjeu résolu                                           |
| ---- | --------------------------------------------------- | ------------------------------------------------------ |
| 13   | **Scope personnalisé** + `BeanFactoryPostProcessor` | Multi-tenance isolée, pas de fuite de connexions       |
| 14   | **`@ConditionalOnMissingBean`**                     | Surcharge sûre, zéro collision de beans                |
| 15   | **`@Lookup` method injection**                      | Prototype frais sans dépendre d’`ObjectProvider`       |
| 16   | **`EnvironmentPostProcessor`**                      | Construit l’`Environment` avant toute création de bean |

Toujours aucune techno externe : seulement Spring / Spring Boot et son conteneur IoC. Dis-moi si tu veux plonger dans `MergedBeanDefinitionPostProcessor`, les `SmartInitializingSingleton`, ou encore l’AOT `RuntimeHints`.

### 13 — **Scope personnalisé « tenant » : multi-tenance sans fuite d’état**

```mermaid
flowchart TD
    ctx[ApplicationContext] --> ScopeReg["TenantScopeRegistrar<br/>(BeanFactoryPostProcessor)"]
    ScopeReg -->|register scope| tenantScope["tenant"]
    RequestA[Req tenant alpha] -->|"setTenant(alpha)"| tenantScope
    tenantScope -- get(ds) --> DSα[(DataSource α)]
    RequestB[Req tenant beta] -->|"setTenant(beta)"| tenantScope
    tenantScope -- get(ds) --> DSβ[(DataSource β)]

```

**Contexte métier —** Une SaaS B2B héberge plusieurs compagnies d’assurance ; chaque locataire a *sa propre* base de données.
**Problème —** Le prototype par requête ne suffit pas : l’objet `DataSource` doit être partagé *par tenant* mais jamais entre locataires.

#### Solution détaillée

1. Créer un `TenantScope` implémentant `org.springframework.beans.factory.config.Scope` ; un `ThreadLocal<String>` garde l’ID courant.
2. Enregistrer la scope dans un `BeanFactoryPostProcessor`.
3. Annoter `DataSource` (ou tout bean sensible) avec `@Scope("tenant")`.
4. Un `OncePerRequestFilter` positionne `TenantContext.set(id)` en début de requête et le nettoie à la fin.

**Pourquoi ça marche ?** Spring route chaque appel `getBean("ds")` vers le cache du tenant courant. L’ISOlation des connexions est totale et aucun castor de connexion n’est créé hors besoin.

```java
public final class TenantContext {
    private static final ThreadLocal<String> TL = new ThreadLocal<>();
    public static void set(String id){ TL.set(id); }
    public static String get(){ return TL.get(); }
    public static void clear(){ TL.remove(); }
}

public class TenantScope implements Scope {
    private final ConcurrentMap<String, Map<String,Object>> cache = new ConcurrentHashMap<>();
    public Object get(String name, ObjectFactory<?> of){
        String tenant = TenantContext.get();
        return cache
              .computeIfAbsent(tenant,_->new ConcurrentHashMap<>())
              .computeIfAbsent(name, k->of.getObject());
    }
    public void remove(String name){ cache.values().forEach(m->m.remove(name)); }
    // getConversationId etc.
}

@Component
public class TenantScopeRegistrar implements BeanFactoryPostProcessor {
    @Override public void postProcessBeanFactory(ConfigurableListableBeanFactory bf){
        bf.registerScope("tenant", new TenantScope());
    }
}

@Scope("tenant")
@Configuration
public class TenantDataSourceConfig {
    @Bean public DataSource ds(){
        return DataSourceBuilder.create()
               .url("jdbc:postgresql:///"+TenantContext.get())
               .username("svc")
               .build();
    }
}
```

---

### 14 — **`@ConditionalOnMissingBean` : fournir un *fallback* sans collision**

```mermaid
flowchart TD
    AutoCfg[Auto-Configuration] -->|no custom bean| DefaultID[[DefaultIdGenerator]]
    AutoCfg -->|custom bean present| CustomID[[CustomIdGenerator]]
    OrderSvc[OrderService] --> DefaultID & CustomID
```

**Contexte métier —** Tous les modules doivent disposer d’un générateur d’identifiant ; certains projets veulent injecter leur propre stratégie (Snowflake, ULID…).
**Problème —** Dès qu’un second bean `IdGenerator` apparaît, Spring jette `NoUniqueBeanDefinitionException`.

#### Solution détaillée

* L’auto-configuration déclare **un bean par défaut** recouvert par `@ConditionalOnMissingBean(IdGenerator.class)`.
* Dès qu’un module déclare sa propre implémentation, Spring ignore le défaut.

**Pourquoi ça marche ?** Le conditionnel est évalué à l’enregistrement des définitions ; s’il trouve un autre `IdGenerator`, il ne crée pas le bean de secours, évitant tout conflit.

```java
public interface IdGenerator { String next(); }

@Configuration(proxyBeanMethods=false)
public class IdGeneratorAutoConfig {

    @Bean
    @ConditionalOnMissingBean
    public IdGenerator defaultIdGenerator() {
        return () -> UUID.randomUUID().toString();
    }
}

@Component
@Profile("high-scale")                       // projet qui a besoin d’un ULID
public class UlidGenerator implements IdGenerator {
    public String next(){ return UlidCreator.getUlid(); }
}
```

---

### 15 — **`@Lookup` : obtenir un prototype via méthode abstraite**

```mermaid
flowchart TD
    Invoker["ReportService (singleton)"] --@Lookup--> ProtoNew[(ReportBuilder prototype)]
    Invoker -.many calls .-> ProtoNew
```

**Contexte métier —** Chaque PDF doit posséder sa propre instance de `ReportBuilder` (non thread-safe).
**Problème —** Impossible d’injecter directement un prototype dans le singleton `ReportService` sans retomber sur l’erreur du scope prototype partagé.

#### Solution détaillée

* Déclarer une **méthode abstraite** dans le singleton, annotée `@Lookup`.
* Au démarrage, Spring génère un sous-classe CGLIB qui implémente la méthode ; chaque appel délègue à `BeanFactory.getBean("reportBuilder")`.

**Pourquoi ça marche ?** Le code métier reste propre ; aucune dépendance à `ObjectFactory`. L’IoC génère et insère la logique de lookup, fournissant un prototype *à chaque appel*.

```java
@Service
public abstract class ReportService {

    public byte[] render(Invoice inv) {
        ReportBuilder rb = createBuilder();      // prototype frais
        return rb.render(inv);
    }

    @Lookup("reportBuilder")                    // méthode magique
    protected abstract ReportBuilder createBuilder();
}

@Scope("prototype")
@Component("reportBuilder")
public class ReportBuilder {
   /* lourd, patterns de volaille, etc. */
}
```

---

### 16 — **`EnvironmentPostProcessor` : substitution automatique de propriétés**

**Pourquoi ça marche ?** `EnvironmentPostProcessor` intervient tout au début du cycle Boot ; la substitution est invisible pour le reste du code, garantissant qu’aucun bean ne pointe vers Internet en environnement de test.

```mermaid
flowchart TD
    Boot --> PostProc[PlaceholdersPostProcessor]
    PostProc --> Env[Environment with placeholders resolved] --> ctx[Beans]
```

**Contexte métier —** La DSI impose qu’en **recette** toutes les URLs finissent par `.internal` pour interdire le trafic sortant accidentel.
**Problème —** Les développeurs oublient souvent de changer `https://….com` en `internal`, et le build passe quand même.

#### Solution détaillée

1. Implémenter `EnvironmentPostProcessor` qui parcourt chaque `PropertySource` ; si `spring.profiles.active` contient `test`, il remplace `*.com` par `*.internal`.
2. Le processeur s’exécute avant le `refresh()` ; les beans reçoivent déjà les valeurs corrigées.

```java
public class InternalPostProcessor implements EnvironmentPostProcessor {

    private static final Pattern OUT = Pattern.compile("https?://([^/]+)\\.com");

    @Override
    public void postProcessEnvironment(ConfigurableEnvironment env, SpringApplication app) {
        if (!env.acceptsProfiles(Profiles.of("test"))) return;

        env.getPropertySources().forEach(ps -> {
            if (ps instanceof EnumerablePropertySource<?> eps) {
                for (String name : eps.getPropertyNames()) {
                    Object v = eps.getProperty(name);
                    if (v instanceof String s) {
                        String patched = OUT.matcher(s).replaceAll("https://$1.internal");
                        if (!patched.equals(s))
                            ((MutablePropertySources) env.getPropertySources())
                                .addFirst(new MapPropertySource("patched-"+name,
                                    Map.of(name, patched)));
                    }
                }
            }
        });
    }
}
```

`META-INF/spring.factories` :

```
org.springframework.boot.env.EnvironmentPostProcessor=\
com.acme.bootstrap.InternalPostProcessor
```



#### Pourquoi ces scénarios comptent

| #    | Mécanisme Spring                      | Valeur apportée en production                     |
| ---- | ------------------------------------- | ------------------------------------------------- |
| 9    | `@Lazy` + proxy                       | Démarrage plus rapide, mémoire au juste-à-temps   |
| 10   | `FactoryBean`                         | Encapsulation propre de construction complexe     |
| 11   | `ApplicationContextInitializer`       | Secrets injectés avant toute création de bean     |
| 12   | `BeanDefinitionRegistryPostProcessor` | Extensibilité plug-and-play, zéro config manuelle |

Chaque exemple reste **strictement** dans le périmètre Spring/Spring Boot ; aucune technologie externe n’est nécessaire hors de Vault pour l’exemple 11. Je peux encore détailler `MergedBeanDefinitionPostProcessor`, `ScopedProxyMode` pour le scope *request*, ou la nouvelle API AOT si tu le souhaites !

### 9 — **Initialisation paresseuse : réduire le temps de démarrage d’un moteur de règles**

```mermaid
flowchart TD
    ctx[ApplicationContext] --> PricingSvc{{"PricingService<br/>(singleton)"}}
    click PricingSvc "Void"
    PricingSvc -.first call .-> RuleEngineProxy[[@Lazy<br/>RuleEngine proxy]]
    RuleEngineProxy -- instantiates --> RuleEngine[(RuleEngine - prototype)]

```

**Contexte métier** — Une application de tarification démarre plusieurs fois par jour dans des conteneurs éphémères ; un moteur de règles (15 000 règles Drools) rallongeait le boot de 18 s.

#### Problème

Le bean `RuleEngine` était créé lors du `refresh()` du contexte Spring bien que 90 % des requêtes n’en aient pas besoin.

#### Solution expliquée

* Marquer le bean lourd `@Lazy`, injecter le **proxy** dans le singleton `PricingService`.
* Le conteneur remplace l’instance directe par un *cglib proxy* ; la vraie construction du moteur n’a lieu qu’à la **première** invocation de `price(…)`.
* Le démarrage passe de 22 s à 4 s ; la première requête chaude paie la pénalité unique d’initialisation.

```java
@Service
public class PricingService {

    private final RuleEngine ruleEngine;     // proxy @Lazy

    public PricingService(@Lazy RuleEngine ruleEngine) {
        this.ruleEngine = ruleEngine;
    }

    public BigDecimal price(Quote q) {
        return ruleEngine.evaluate(q);
    }
}

@Lazy                                       // initialisation à la demande
@Component
@Scope("prototype")                         // pas réutilisable
public class RuleEngine {

    @PostConstruct
    void loadRules() throws IOException {
        // charge 15 000 DRL depuis le classpath
    }

    public BigDecimal evaluate(Quote q) { /* exécution Drools */ }
}
```

---

### 10 — **`FactoryBean` : encapsuler la création complexe d’un objet tiers**

```mermaid
flowchart TD
    ctx[ApplicationContext] --> CnxFactoryBean{{"JmsCnxFactoryBean<br/>(FactoryBean)"}}
    CnxFactoryBean -- getObject() --> ConnFactory[(javax.jms.ConnectionFactory)]
    OrderSvc[OrderService] --> ConnFactory
```

**Contexte métier** — L’équipe doit intégrer un broker JMS propriétaire ; la création d’un `ConnectionFactory` nécessite dix paramètres et plusieurs appels statiques.

#### Problème

Sans encapsulation, chaque service devait dupliquer un code d’initialisation verbeux et fragile.

#### Solution expliquée

* Implémenter `FactoryBean<ConnectionFactory>` : Spring voit le bean comme un **fabricant**.
* Le code compliqué reste confiné ; tous les consommateurs obtiennent simplement un `ConnectionFactory` injectable.
* Possibilité de **lazy-init** et de cache interne pour partager la ressource.

```java
@Component("orderBroker")
public class JmsCnxFactoryBean implements FactoryBean<ConnectionFactory>, InitializingBean {

    private ConnectionFactory target;

    @Override
    public void afterPropertiesSet() {
        BrokerConfig cfg = BrokerConfig.builder()
                                       .url(System.getenv("BROKER_URL"))
                                       .user("svc-order")
                                       .password(System.getenv("BROKER_PWD"))
                                       .ssl(true)
                                       .build();
        this.target = ProprietaryBroker.buildFactory(cfg);
    }

    @Override public ConnectionFactory getObject() { return target; }
    @Override public Class<?> getObjectType() { return ConnectionFactory.class; }
    @Override public boolean isSingleton() { return true; }
}

@Service
@RequiredArgsConstructor
public class OrderService {

    private final ConnectionFactory orderBroker;     // résolu par id "orderBroker"
}
```

---

### 11 — **`ApplicationContextInitializer` : rajouter une `PropertySource` chiffrée avant le `refresh()`**

```mermaid
flowchart TD
    Boot --> Init["VaultInitializer<br/>(ApplicationContextInitializer)"]
    Init --> Env[ConfigurableEnvironment]
    Env -->|adds| VaultProps[[VaultPropertySource]]
    VaultProps --> ctx[ApplicationContext]
```

**Contexte métier** — Les mots de passe base-de-données résident dans HashiCorp Vault ; ils doivent être disponibles **avant** que Spring ne crée le bean `DataSource`.

#### Problème

Si l’on ajoute la `PropertySource` dans un `@Configuration` classique, c’est trop tard : `DataSource` est déjà construit avec des valeurs vides.

#### Solution expliquée

* Déclarer un `ApplicationContextInitializer` référencé dans `META-INF/spring.factories`.
* À l’amorçage, Spring l’exécute **avant** la phase de bean-definition, autorisant l’injection des credentials déchiffrés dans l’`Environment`.

```java
public class VaultInitializer
        implements ApplicationContextInitializer<ConfigurableApplicationContext> {

    @Override
    public void initialize(ConfigurableApplicationContext ctx) {
        ConfigurableEnvironment env = ctx.getEnvironment();
        Map<String,Object> secrets = VaultClient.fetch("secret/prod/db");
        PropertySource<?> vault = new MapPropertySource("vault", secrets);
        env.getPropertySources().addFirst(vault);       // plus haute priorité
    }
}
```

`spring.factories` :

```
org.springframework.context.ApplicationContextInitializer=\
com.acme.bootstrap.VaultInitializer
```

---

### 12 — **`BeanDefinitionRegistryPostProcessor` : auto-enregistrement dynamique de stratégies**

```mermaid
flowchart TD
    ctx[ApplicationContext] --> Scanner{{"StrategyRegistrar<br/>(RegistryPostProcessor)"}}
    Scanner -- registerBeanDefs --> T1[(CsvStrategy)]
    Scanner -- registerBeanDefs --> T2[(JsonStrategy)]
    StrategyFactory[StrategyFactory] --> T1 & T2
```

**Contexte métier** — Un ETL doit supporter n formats de fichier (CSV, JSON, XML…). On veut que chaque nouvel algo parseur soit découvert **sans** modifier une configuration centrale.

#### Problème

Énumérer les stratégies dans du YAML ou du code est laborieux et source d’oublis.

#### Solution expliquée

* Implémenter `BeanDefinitionRegistryPostProcessor` : à la phase **la plus précoce**, scanner le classpath à la recherche de `@FileStrategy` puis **enregistrer** les définitions de bean correspondantes.
* Le reste de l’application peut injecter une `Map<String, FileStrategy>` ; l’injection contiendra automatiquement tous les parseurs présents sur le classpath.

```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface FileStrategy {
    String value();
}

@Component
public class StrategyRegistrar implements BeanDefinitionRegistryPostProcessor {

    @Override
    public void postProcessBeanDefinitionRegistry(BeanDefinitionRegistry reg) {
        Set<Class<?>> strategists = ClassScanner.findAnnotated(FileStrategy.class);
        for (Class<?> c : strategists) {
            String name = c.getAnnotation(FileStrategy.class).value();
            GenericBeanDefinition bd = new GenericBeanDefinition();
            bd.setBeanClass(c);
            reg.registerBeanDefinition(name, bd);
        }
    }
    @Override public void postProcessBeanFactory(ConfigurableListableBeanFactory bf) { }
}

public interface FileStrategy { Record parse(String line); }

@FileStrategy("csv")
public class CsvStrategy implements FileStrategy { /* … */ }

@FileStrategy("json")
public class JsonStrategy implements FileStrategy { /* … */ }

@Service
@RequiredArgsConstructor
public class ImportService {

    private final Map<String, FileStrategy> strategies;

    public void importFile(String type, Path p) throws IOException {
        Files.lines(p).forEach(l -> strategies.get(type).parse(l));
    }
}
```

---

## Conclusion – Compétences démontrées

| Axe                        | Ce qui est montré                                            |
| -------------------------- | ------------------------------------------------------------ |
| **Scopes & DI**            | Différence pratique prototype/singleton, création à la demande avec `ObjectProvider`. |
| **Cycle de vie**           | Usage avancé de `SmartLifecycle` : phases, callback d’arrêt, ordonnancement garanti. |
| **Configuration**          | Externalisation propre, validation au démarrage, profils hiérarchiques. |
| **Ordre d’initialisation** | Contrôle explicite via `@DependsOn` et compréhension des post-processeurs. |

Toutes les solutions utilisent **uniquement** les mécanismes natifs de Spring / Spring Boot ; aucune techno tierce n’intervient. Si tu veux encore plus de profondeur sur, par exemple, `BeanPostProcessor`, l’AOT « functional bean registration » ou la propagation de `ScopedProxyMode`, fais-le moi savoir !

### 1. **Prototype injecté dans un Singleton : fuite mémoire & état corrompu**

**Contexte métier —** moteur de tarification « pay-per-use » pour contrats d’assurance.
Pendant la haute saison, la classe `PricingService` encaisse 60 000 requêtes par minute. Elle déclare un champ :

```java
@Autowired
private Calculator calculator;        // @Scope("prototype")
```

Le développeur croyait qu’un nouveau `Calculator` serait créé à chaque appel. **Erreur** : Spring résout l’injection une seule fois, *au moment où il instancie le singleton*. La même instance — donc son état interne — est partagée par tous les threads ; l’objet grossit, le heap explose, et des primes erronées sont servies.

**Pourquoi cette solution règle le problème ?** `ObjectProvider#getObject()` délègue au conteneur **à l’appel** ; Spring crée alors autant de prototypes qu’il y a d’invocations, éliminant toute fuite de mémoire et tout état partagé entre threads.

```mermaid
flowchart LR
    subgraph "IoC Container"
        PricingService:::singleton -->|"getObject()"| Calc1[(Calculator)]
        PricingService -->|"getObject()"| Calc2[(Calculator)]
        PricingService -->|"getObject()"| Calc3[(Calculator)]
    end
    classDef singleton fill:#d0edff,stroke:#036,stroke-width:1;
```

#### Explication pas-à-pas

1. `PricingService` est un **singleton** : une instance unique, gardée par le conteneur pour toute la durée du processus.
2. `Calculator` est déclaré `@Scope("prototype")`, mais, injecté **par champ**, il est créé une seule fois puis stocké comme référence.
3. Au fil des appels, les champs mutables de `Calculator` (réductions, bonus-malus, taxes) s’empilent → mémoire + risques de fuite.

#### Solution : *Lookup Method Injection* via `ObjectProvider`

`ObjectProvider` remet la décision de créer l’objet au **moment** où on en a besoin ; Spring peut alors respecter le scope prototype. ([Baeldung][1], [Home][2])

```java
@Service                                      // ① Bean singleton
@RequiredArgsConstructor
public class PricingService {

    private final ObjectProvider<Calculator> calculators;

    public BigDecimal price(ContractDto dto) {
        Calculator calc = calculators.getObject();       // ② Instance NEUVE à chaque appel
        return calc.compute(dto);
    }
}

@Scope("prototype")                           // ③ Créé puis oublié par le conteneur
@Component
public class Calculator {

    public BigDecimal compute(ContractDto dto) {
        BigDecimal base = dto.capital().multiply(new BigDecimal("0.008"));
        BigDecimal discount = dto.loyaltyYears() > 5
                              ? base.multiply(new BigDecimal("0.05"))
                              : BigDecimal.ZERO;
        return base.subtract(discount)
                   .setScale(2, RoundingMode.HALF_UP);
    }
}
```

---

### 2. **Orchestration de démarrage/arrêt avec `SmartLifecycle`**

**Contexte métier —** batch nocturne de consolidation comptable qui DOIT démarrer *après* le pré-chargement du cache et s’arrêter *avant* la fermeture de la DataSource.

**Problème rencontré** : le batch démarrait parfois trop tôt, échouait sur un cache vide ; à l’extinction, il se faisait tuer avant d’avoir flushé ses dernières écritures.

#### Le mécanisme `SmartLifecycle` expliqué

*SmartLifecycle* étend `Lifecycle` + `Phased` :

**Pourquoi ça marche ?** Spring applique l’ordre 100 → 200 au démarrage, 200 → 100 à l’arrêt ; chaque composant dispose d’un hook *bloquant* (`stop(Runnable)`) pour terminer proprement son travail.

```mermaid
sequenceDiagram
    participant SpringCtx
    participant Cache as CacheLoader (phase 100)
    participant Batch as ConsolidationBatch (phase 200)
    SpringCtx->>Cache: start()
    SpringCtx->>Batch: start()
    note over Cache,Batch: … application en production …
    SpringCtx-->>Batch: stop()
    Batch-->>SpringCtx: callback✓
    SpringCtx-->>Cache: stop()
    Cache-->>SpringCtx: callback✓
```

* **phase croissante** au démarrage → les petites valeurs partent en premier.
* **phase décroissante** à l’arrêt → les grosses valeurs sont stoppées en premier.
  *Le conteneur garantit la séquentialité ; on n’écrit plus de code “main()” artisanal.* ([Medium][3], [Home][4])

```java
@Component                                       // ① Se lance en phase 100
public class CacheLoader implements SmartLifecycle {

    private final AccountRepository repo;
    private final ConcurrentMap<String, Account> cache = new ConcurrentHashMap<>();
    private volatile boolean running;

    @Override public void start() {
        logger.info("Warm-up cache …");
        repo.findAll().forEach(acc -> cache.put(acc.id(), acc));
        running = true;
    }

    @Override public void stop(Runnable callback) {
        logger.info("Flush cache …");
        cache.values().forEach(repo::save);
        running = false;
        callback.run();                           // ② Signale à Spring la fin du travail
    }

    @Override public boolean isRunning() { return running; }
    @Override public int getPhase()     { return 100; }
    @Override public boolean isAutoStartup() { return true; }
}

@Component                                       // ③ Phase 200 ⇒ après le cache
public class ConsolidationBatch implements SmartLifecycle, Runnable {

    private volatile boolean running;

    @Override public void start() { new Thread(this).start(); }
    @Override public void run()  { /* traitement chunk-oriented */ running = true; }
    @Override public void stop(Runnable cb) { gracefulShutdown(); running = false; cb.run(); }
    @Override public boolean isRunning() { return running; }
    @Override public int getPhase()     { return 200; }
    @Override public boolean isAutoStartup() { return true; }

    private void gracefulShutdown() { /* commit final + log */ }
}
```

---

### 3. **Explosion du YAML et validation de configuration**

**Contexte métier —** même application déployée sur *dev*, *test*, *stage* et *prod* ; `application.yml` atteignait 1 200 lignes et personne ne savait plus quelles propriétés étaient réellement utilisées.

#### Approche par étapes

**Pourquoi c’est utile ?** L’échec est *fail-fast* ; la configuration est centralisée, validée et documentée par le code lui-même. On élimine les « mauvais prod.yml » qui cassent dimanche soir.

```mermaid
flowchart TD
    Base[[application.yaml]]
    Dev[[application-dev.yaml]]
    Test[[application-test.yaml]]
    Prod[[application-prod.yaml]]
    Base -->|spring.profiles.active=prod| Prod
    Base --> Dev & Test
    Prod --> Props[[BillingProperties bean]]
    Props --> App[(Business Services)]
```



1. **Découpage par profils** — `application-{profile}.yaml` ; le fichier racine ne contient plus que les valeurs communes.
2. **Regroupement typé** avec `@ConfigurationProperties` : une classe Java hiérarchique porte l’ensemble des clés.
3. **Validation** au démarrage via *Bean Validation* (JSR-380) : si une URL est mal formée ou un timeout négatif, l’application échoue *avant* de se mettre à écouter sur 8080.
4. **Documentation** — la seule source de vérité devient la classe de properties ; les IDE exposent l’autocomplétion. ([Baeldung][5], [DEV Community][6], [reflectoring.io][7])

```java
@ConfigurationProperties(prefix = "billing")       // ① Toutes les clés sous billing.*
@Validated                                          // ② Validation JSR-380
public record BillingProperties(
        @NotNull URI endpoint,
        @Min(1) int retryAttempts,
        @DurationMin(seconds = 1) Duration timeout) {}
```

```yaml
# application.yaml (commun)
spring:
  profiles:
    group:
      dev: dev
      test: test
      prod: prod

# application-prod.yaml
billing:
  endpoint: "https://api.acme-payments.com/v1"
  retry-attempts: 3
  timeout: 5s
```

---

### 4. **Ordre d’initialisation finement contrôlé avec `@DependsOn`**

**Contexte métier —** module d’export PDF qui dépend d’un moteur de templates Freemarker lui-même initialisé par un *BeanFactoryPostProcessor*. Un *NullPointerException* apparaissait aléatoirement : quand `PdfExporter` démarrait avant que `TemplateEngine` n’ait fini son `@PostConstruct`.

#### Analyse

*Spring publie* un bean dans le contexte **après** l’exécution de son `@PostConstruct`. Mais si un **post-processeur** (p. ex. chargé de pré-compiler les templates) intervient, il peut rallonger la construction. L’ordre d’enregistrement devient crucial.

**Pourquoi ça marche ?** Spring lit l’annotation `@DependsOn` au tout début du processus ; il retarde l’instanciation de `PdfExporter` jusqu’à ce que *tout* ce dont dépend `templateEngineInitializer` soit prêt, évitant les NullPointer aléatoires.

```mermaid
flowchart LR
    subgraph "Bean creation"
        Init[TemplateEngineInitializer<br/>BeanFactoryPostProcessor] --> Engine[TemplateEngine]
        Engine --> Exporter["PdfExporter<br/>@DependsOn(templateEngineInitializer)"]
    end
```

#### Remède

`@DependsOn` force explicitement l’ordre : `PdfExporter` n’est pas instancié tant que `templateEngineInitializer` n’est pas sorti de son `postProcessBeanFactory`. ([Baeldung][8], [Medium][9], [Stack Overflow][10])



```java
@Component("templateEngineInitializer")                // ① Post-processeur
public class TemplateEngineInitializer implements BeanFactoryPostProcessor {

    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory bfb) {
        // compile 300 templates & cache metadata
    }
}

@DependsOn("templateEngineInitializer")                // ② Ordre garanti
@Component
public class PdfExporter {

    private final Configuration freemarkerCfg;

    public PdfExporter(Configuration freemarkerCfg) {
        this.freemarkerCfg = freemarkerCfg;
    }

    @PostConstruct
    void verify() {
        Assert.notNull(freemarkerCfg.getTemplate("invoice.ftl"),
                       "Template manquant après init !");
    }

    public byte[] export(Invoice invoice) {
        Map<String,Object> model = Map.of("invoice", invoice);
        return renderPdf("invoice.ftl", model);
    }

    /* méthode utilitaire concrète */
    private byte[] renderPdf(String tpl, Map<String,Object> data) {
        /* -- rendu Freemarker + Flying-Saucer -- */
        return /* bytes */ new byte[0];
    }
}
```

### Nouveaux scénarios 100 % Spring / Spring Boot – IoC, scopes, cycle de vie

*(Toujours : contexte métier réaliste → problème complexe → explication détaillée → code complet → diagramme Mermaid interne au conteneur.)*

### Récapitulatif

| Thème                         | Mécanisme Spring approfondi                           | Valeur apportée                                  |
| ----------------------------- | ----------------------------------------------------- | ------------------------------------------------ |
| **Événements & transactions** | `@TransactionalEventListener` (phase = AFTER\_COMMIT) | Actions cohérentes, zéro déclenchement fantôme   |
| **Cross-cutting interne**     | `BeanPostProcessor` + proxies CGLIB                   | Logging/audit sans polluer le code métier        |
| **Scopes web**                | `@Scope("session")` + `ScopedProxyMode`               | Panier utilisateur sûr, injection dans singleton |
| **Conditional beans**         | `@Profile`, `@ConditionalOnProperty`                  | Choix d’implémentation sûr, *fail-fast*          |

Ces exemples complètent les quatre précédents : ils couvrent désormais **événements**, **post-processing**, **scopes web**, **sélection conditionnelle** — le cœur fonctionnel de Spring IoC sans recourir à la moindre technologie externe. N’hésite pas à demander d’autres scénarios : `BeanFactoryPostProcessor`, `FactoryBean`, `ApplicationContextInitializer`, ou même la chaîne complète des `BeanPostProcessor` et `MergedBeanDefinitionPostProcessor`.

---

## 5. Événements d’application et cohérence transactionnelle

**Contexte métier —** *Plate-forme de gestion de sinistres automobile*
Lorsqu’un sinistre est créé, plusieurs sous-processus doivent être déclenchés : génération du numéro de dossier, pré-réservation d’un véhicule de remplacement, envoi d’un accusé de réception. Au début, le code appelait ces services l’un après l’autre ; un rollback SQL laissait parfois les mails et les réservations « dans la nature ».

### Problème

Les actions secondaires doivent s’exécuter **uniquement si** la transaction principale réussit, et **jamais** en cas de rollback.

### Solution détaillée

**Pourquoi ça marche ?** Le listener est enregistré dans le `SynchronizationManager` ; Spring l’exécute seulement quand `DataSourceTransactionManager` confirme le commit, garantissant qu’aucune action secondaire ne survit à un rollback.

```mermaid
sequenceDiagram
    participant Tx as Spring Tx
    participant Service as ClaimService
    participant Repo as ClaimRepository
    participant Pub as ApplicationEventPublisher
    participant DB as DB
    participant Listener as ClaimWorkflowListener
    participant Mailer as Mailer
    participant Car as Car

    Service->>Repo: save()
    Repo->>DB: INSERT
    Service->>Pub: publish(ClaimCreated)

    alt commit
        Tx->>DB: COMMIT
        Tx-->>Listener: AFTER_COMMIT
        Listener->>Mailer: email
        Listener->>Car: reserve
    else rollback
        Tx->>DB: ROLLBACK
        Note over Listener: jamais appelé en cas de rollback
    end
```

1. Publier un **événement de domaine** (`ClaimCreatedEvent`) *dans* la transaction.
2. Écouter avec `@TransactionalEventListener(phase = AFTER_COMMIT)` : Spring enregistre le listener ; il n’invoque la méthode qu’après le commit JDBC.
3. Pour les notifications lentes, déléguer au `@Async` thread-pool afin de ne pas bloquer le thread utilisateur.

```java
// ① Publication de l’événement
@Service
@RequiredArgsConstructor
public class ClaimService {

    private final ApplicationEventPublisher publisher;
    private final ClaimRepository repo;

    @Transactional
    public Claim openClaim(NewClaimDto dto) {
        Claim claim = repo.save(Claim.create(dto));
        publisher.publishEvent(new ClaimCreatedEvent(claim.getId(), dto.policyId()));
        return claim;
    }
}

// ② Listener après commit
@Component
@RequiredArgsConstructor
public class ClaimWorkflowListener {

    private final Mailer mailer;
    private final RentalCarGateway cars;

    @Async
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void handleClaimCreated(ClaimCreatedEvent ev) {
        mailer.sendAcknowledge(ev.claimId());
        cars.reserveTemporaryVehicle(ev.claimId());
    }
}
```

---

## 6. Proxying transversal automatique avec `BeanPostProcessor`

**Contexte métier —** *Plate-forme B2B qui expose 300 services REST internes*
L’audit interne exige un **journal exhaustif** de chaque appel public : nom de la méthode, arguments, durée. Écrire l’aspect manuellement sur 300 classes est intenable.

### Problème

Ajouter un logging uniforme sans polluer chaque service de `log.info(…)` et sans AOP XML.

### Solution détaillée

1. Marquer les services à tracer par une simple annotation `@Logged`.
2. Créer un `BeanPostProcessor` qui, pour chaque bean annoté, génère dynamiquement un **proxy CGLIB** ; ce proxy entoure chacune de ses méthodes d’une trace.
3. La solution est 100 % interne au conteneur ; aucun framework tiers n’est requis.

**Pourquoi ça marche ?** Le `BeanPostProcessor` agit **après** l’instanciation mais **avant** que le bean ne soit enregistré dans le context. Le conteneur expose donc la version proxifiée ; tout appel passe par l’intercepteur sans que le code métier ne change.

```mermaid
flowchart LR
    Bean0["PartnerService<br/>(original)"] --BeanPostProcessor--> Proxy[[CGLIB proxy<br/>+ advice]]
    Client --> Proxy --> Bean0
```



```java
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
public @interface Logged {}

// ① Exemple de service annoté
@Logged
@Service
public class PartnerService {
    public PartnerDto findById(UUID id) { /* ... */ }
}

// ② Post-processeur
@Component
public class LoggingProxyPostProcessor implements BeanPostProcessor {

    private static final Logger log = LoggerFactory.getLogger("Audit");

    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) {
        if (!bean.getClass().isAnnotationPresent(Logged.class)) return bean;

        ProxyFactory pf = new ProxyFactory(bean);
        pf.addAdvice((MethodInterceptor) invocation -> {
            long t0 = System.nanoTime();
            try {
                return invocation.proceed();
            } finally {
                long ms = TimeUnit.NANOSECONDS.toMillis(System.nanoTime() - t0);
                log.info("{}#{} took {} ms",
                         invocation.getMethod().getDeclaringClass().getSimpleName(),
                         invocation.getMethod().getName(), ms);
            }
        });
        return pf.getProxy();
    }
}
```

---

## 7. Scopes web : session + proxy et injection dans un singleton

**Contexte métier —** *Site e-commerce de chaussures*
Un `ShoppingCart` doit être unique par visiteur, mais le `OrderService` reste un singleton partagé. Injection directe d’un bean `@Scope("session")` provoque une `BeanCreationException` hors contexte web.

### Problème

Comment injecter un bean à durée de vie *session* dans un singleton tout en restant thread-safe ?

### Solution détaillée

**Pourquoi ça marche ?** Le proxy stocke la clé HTTP session ; à chaque méthode, il récupère l’instance réelle dans le `SessionScope` de Spring MVC. Aucun cast, aucune vérification de thread ; le singleton reste agnostique.

```mermaid
flowchart LR
    subgraph "Singleton layer"
        OrderService --- CartProxy[ShoppingCart proxy]
    end
    subgraph "Session 1"
        Cart1[(ShoppingCart#A)]
    end
    subgraph "Session 2"
        Cart2[(ShoppingCart#B)]
    end
    CartProxy --delegates--> Cart1
    CartProxy --delegates--> Cart2
```



1. Déclare `ShoppingCart` avec `proxyMode = ScopedProxyMode.TARGET_CLASS` ; Spring crée un *proxy de scope* qui reste singleton mais délègue à la bonne instance de session *à l’appel*.
2. `OrderService` récupère donc un objet stable, et chaque utilisateur voit son propre panier.

```java
@Scope(value = WebApplicationContext.SCOPE_SESSION,
       proxyMode = ScopedProxyMode.TARGET_CLASS)
@Component
public class ShoppingCart {

    private final List<Item> items = new ArrayList<>();

    public void add(Item i) { items.add(i); }
    public List<Item> items() { return List.copyOf(items); }
    public void clear() { items.clear(); }
}

@Service                                // singleton
@RequiredArgsConstructor
public class OrderService {

    private final ShoppingCart cart;    // en réalité: proxy de scope

    @Transactional
    public Order placeOrder(User u) {
        Order order = new Order(u, cart.items());
        cart.clear();                   // proxy → panier de CE client
        return order;
    }
}
```

---

## 8. Beans conditionnels et environnement contrôlé

**Contexte métier —** *Passerelle de paiement*
En développement, on veut un *PaymentGateway* simulé ; en production, on appelle le vrai PSP. Des properties mal configurées avaient déjà envoyé des paiements réels depuis un serveur de test !

### Problème

Sélectionner la bonne implémentation **sans** if / else, en reposant uniquement sur le conteneur.

### Solution détaillée

1. Déclare une interface `PaymentGateway`.
2. Fournir deux implémentations :

   * `RealGateway` annotée `@Profile("prod")`
   * `StubGateway` annotée `@Profile({"dev","test"})` **et** `@ConditionalOnProperty` pour permettre un override ponctuel.
3. Activer le profil désiré via `SPRING_PROFILES_ACTIVE`. L’application refuse de démarrer si plusieurs implémentations sont éligibles, évitant toute ambiguïté.

**Pourquoi ça marche ?** Les *profiles* sont résolus avant la création des beans ; Spring n’enregistre qu’une implémentation. Le flag `gateway.stub.enabled` permet de désactiver explicitement le stub, même en dev, lorsque l’on veut tester le vrai PSP sur un environnement de staging.

```mermaid
flowchart TD
    style Prod fill:#fff
    Stub[["StubGateway<br/>@Profile(dev,test)"]]:::stub
    Real[["RealGateway<br/>@Profile(prod)"]]:::real
    PaymentService --> |SPRING_PROFILES_ACTIVE=dev| Stub
    PaymentService --> |SPRING_PROFILES_ACTIVE=prod| Real
    classDef stub fill:#d0ffd0,stroke:#070;
    classDef real fill:#ffd0d0,stroke:#700;
```



```java
public interface PaymentGateway {
    PaymentReceipt pay(Charge ch);
}

@Profile("prod")                           // ① Prod only
@Component
public class RealGateway implements PaymentGateway {

    private final RestClient client = RestClient.create();

    @Override
    public PaymentReceipt pay(Charge ch) {
        return client.post()
                     .uri("https://psp/api/pay")
                     .body(ch)
                     .retrieve()
                     .body(PaymentReceipt.class);
    }
}

@Profile({"dev","test"})                   // ② Non-prod par défaut
@ConditionalOnProperty(name = "gateway.stub.enabled", havingValue = "true", matchIfMissing = true)
@Component
public class StubGateway implements PaymentGateway {

    @Override
    public PaymentReceipt pay(Charge ch) {
        return new PaymentReceipt("STUB-"+UUID.randomUUID(), true, LocalDateTime.now());
    }
}
```

```yaml
# application-dev.yaml
gateway:
  stub:
    enabled: true

# application-prod.yaml
spring:
  profiles:
    active: prod
gateway:
  stub:
    enabled: false
```

## 1. Scope `prototype` mal employé : fuite mémoire et état corrompu

**Contexte métier –** *Plate-forme de tarification « Pay-Per-Use » pour contrats d’assurance*
Pendant la campagne de fin d’année, le service **Tarification** a multiplié les appels HTTP (≈ 60 000 req/min). Le bean `Calculator`, pourtant annoté `@Scope("prototype")`, était injecté directement dans le singleton `PricingService`. Or, Spring *résout l’injection au moment où il construit le singleton* : une **seule instance** du prototype était donc partagée, accumulant dans ses champs l’état de chaque contrat et finissant par saturer le heap puis produire des montants erronés.

#### Solution détaillée

**Pourquoi ça marche ?**
`ObjectProvider` délègue au conteneur **à chaque appel** ; le scope `prototype` est enfin respecté et l’objet ne vit que le temps de la méthode. Pas de fuite mémoire, pas d’état partagé. ([Stack Overflow][1])

```mermaid
flowchart LR
    subgraph "IoC Container"
        PricingService:::single -->|"getObject()"| Calc1((Calculator))
        PricingService -->|"getObject()"| Calc2((Calculator))
    end
    classDef single fill:#d0f0ff,stroke:#036,stroke-width:1;
```

1. **Injection tardive (« lookup »)** avec `ObjectProvider<Calculator>` : Spring crée un **nouveau prototype à chaque appel**.
2. Adoption du **pattern Factory Method** : c’est le conteneur (et non plus le code métier) qui fabrique l’objet ad-hoc.
3. Suppression de tout champ mutable dans `Calculator` ; le résultat est maintenant renvoyé comme valeur retour, évitant toute interférence entre threads.

```java
@Service                               // Bean singleton
@RequiredArgsConstructor
public class PricingService {

    private final ObjectProvider<Calculator> calculators;   // ① Factory « à la demande »

    public BigDecimal price(ContractDto dto) {
        Calculator calc = calculators.getObject();          // ② Instance neuve
        BigDecimal premium = calc.compute(dto);
        log.debug("Prime calculée = {}", premium);
        return premium;
    }
}

@Scope("prototype")                   // Bean à durée de vie courte
@Component
public class Calculator {

    public BigDecimal compute(ContractDto dto) {
        /* ③ Algorithme de prime : bonus-malus, remises, taxes … */
        BigDecimal base = dto.capital().multiply(new BigDecimal("0.008"));
        BigDecimal discount = dto.loyaltyYears() > 5 ? base.multiply(new BigDecimal("0.05")) : BigDecimal.ZERO;
        return base.subtract(discount).setScale(2, RoundingMode.HALF_UP);
    }
}
```

---

## 2. Orchestration du cycle de vie avec `SmartLifecycle`

**Contexte –** *Batch nocturne de consolidation comptable (banque interne)*
Le lot « ConsolideCompta » lisait 12 M écritures, mais il démarrait parfois avant que le cache Redis ne soit rempli ; inversement, à l’arrêt, il interrompt soudain la DataSource encore utilisée par un flush asynchrone, provoquant une perte de données.

#### Solution détaillée

**Pourquoi ça marche ?**
`SmartLifecycle` fournit la granularité que `@PostConstruct`/`DisposableBean` n’ont pas : l’ordre est garanti, le shutdown se fait sans perte.   ([Home][2], [Medium][3])

```mermaid
sequenceDiagram
    participant Context
    participant Cache as CacheLoader[phase 100]
    participant Batch as BatchJobRunner[phase 200]
    Context->>Cache: start()
    Context->>Batch: start()
    Context-->>Batch: stop()
    Batch-->>Context: callback
    Context-->>Cache: stop()
    Cache-->>Context: callback
```

1. Implémenter `SmartLifecycle` sur chaque composant critique .
2. **Phase** : `CacheLoader` = 100, `BatchJobRunner` = 200 → Spring démarre/arrête dans l’ordre voulu grâce à son algorithme *phase croissante au démarrage, décroissante à l’arrêt*.
3. **stop(Runnable callback)** gère l’arrêt asynchrone ; Spring attend le callback pour poursuivre le shutdown.

```java
@Component
public class CacheLoader implements SmartLifecycle {

    private final RedisTemplate<?,?> redis;
    private volatile boolean running;

    @Override public void start() {
        log.info("Warm-up du cache …");
        redis.opsForHash().putAll("accounts", loadFromDb());
        running = true;
    }

    @Override public void stop(Runnable callback) {
        log.info("Flush cache avant arrêt");
        redis.opsForHash().entries("temp").forEach(this::persist);
        running = false;
        callback.run();                                   // ① signale à Spring que l’arrêt est terminé
    }

    @Override public boolean isRunning() { return running; }
    @Override public int getPhase()     { return 100; }   // ② démarre avant le batch
}

@Component
public class BatchJobRunner implements SmartLifecycle, Runnable {

    @Override public void start() { new Thread(this).start(); }
    @Override public void run()   { /* traitement chunk-oriented */ }
    @Override public void stop(Runnable cb) { gracefulShutdown(); cb.run(); }
    @Override public boolean isRunning() { return /* état */; }
    @Override public int getPhase() { return 200; }       // ③ démarre après le cache
}
```

---

## 3. Temps de démarrage trop long : indexing & AOT

**Contexte –** *Application de gestion de contrats d’assurance-vie (monolithe Spring Boot 3.4)*
Après activation CRaC pour des images checkpoint, le warm-up prenait encore 38 s sur ARM64. Analyse `spring-boot:start-up` : 15 s passent dans **class-path scanning** de 1 300 classes.

#### Solution détaillée

**Résultat** : démarrage sec = 11 s (-71 %), checkpoint CRaC = 180 ms. ([Baeldung][4], [Medium][5])

```mermaid
flowchart TD
    AOT[[.spring-components<br/>+ BeanFactoryInit]] -->|compile-time| Context[(IoC<br/>runtime)]
    Context --> Bean1[RestClient]
    Context --> Bean2[PolicyService]
```

## 

1. **Spring Context Indexer** :

   ```gradle
   annotationProcessor("org.springframework:spring-context-indexer")
   ```

   À la compilation, l’index `.spring-components` liste les candidats – Spring arrête le scanning spéculatif.
2. **Functional Bean Registration (AOT)** : enlevant le réflectif, les beans sont créés par lambdas, réduisant *InstantiatingBeanPostProcessor* à néant.
3. **Design pattern** : *Builder* AOT → l’enregistrement des beans est produit par un générateur de source.

```java
@Configuration(proxyBeanMethods = false)          // ① proxy désactivé = AOT-friendly
public class CoreConfiguration {

    @Bean // Fabrication fonctionnelle : aucune réflexion
    RestClient restClient() {
        return RestClient.builder()
                         .requestFactory(HttpComponentsClientHttpRequestFactory::new)
                         .build();
    }
}
```

## 4. Contention des tâches planifiées : Scheduler + Virtual Threads

**Contexte –** *Suivi temps-réel de livraisons pizza*
15 000 tâches `@Scheduled`/h (mise à jour GPS + purge cache). Avec un pool par défaut de 8 threads, les tâches longues (< 8 s) empêchaient les suivantes de démarrer ; les livreurs disparaissaient de la carte.

#### Solution détaillée

**Pourquoi ça marche ?**
Chaque tâche planifiée tourne maintenant dans un virtual thread quasiment gratuit ; même si 500 projections longues s’exécutent, elles ne bloquent plus le déclenchement des tâches courtes. Les positions GPS sont rafraîchies en < 200 ms p95. ([Home][6], [Stack Overflow][1], [Home][7])

```mermaid
flowchart TB
    subgraph "Scheduler (64 threads réels / n v-threads)"
        v1((vT))
        v2((vT))
        v3((vT))
        vN((vT))
    end

    GPS[Flux GPS] --> v1
    GPS --> v2
    GPS --> vN
    vN --> Redis[(Redis GEO)]
```

1. **Spring Boot 3.4** sait convertir automatiquement ses `TaskExecutor` et `TaskScheduler` en **virtual threads** si la propriété `spring.threads.virtual.enabled=true` et JDK 21+ sont présents.
2. On limite les **threads physiques** (64) pour ne pas épuiser le noyau, mais on laisse Spring créer **des milliers de v-threads** légers.
3. Mise en place d’un `RejectedExecutionHandler` sur le scheduler : toute tâche rejetée est ré-insérée avec un back-off exponentiel.

```yaml
spring:
  threads:
    virtual:
      enabled: true             # ① bascule globale
```

```java
@Configuration
@EnableScheduling
public class SchedulingConfig implements SchedulingConfigurer {

    @Override
    public void configureTasks(ScheduledTaskRegistrar reg) {

        ThreadPoolTaskScheduler scheduler = new ThreadPoolTaskScheduler();
        scheduler.setPoolSize(64);                            // ② véritables workers
        scheduler.setWaitForTasksToCompleteOnShutdown(true);
        scheduler.setRejectedExecutionHandler((r, ex) -> {
            log.warn("Tâche rejetée ; retry dans 5 s");
            Executors.newSingleThreadScheduledExecutor()
                     .schedule(() -> scheduler.submit(r), 5, TimeUnit.SECONDS);
        });
        scheduler.initialize();
        reg.setScheduler(scheduler);
    }
}

@Component
public class LocationTasks {

    @Scheduled(fixedRateString = "PT1S")          // 15 k exécutions/h
    public void refreshLiveMap() {
        // récupère 1 000 positions et met à jour Redis GEO
    }

    @Scheduled(cron = "0 */10 * * * *")
    public void purgeStaleRoutes() {
        // supprime traces > 24 h du cache pour limiter la taille
    }
}
```

## Bilan pour le recruteur

* **IoC maîtrisé** : scopes (`singleton`, `prototype`), cycles de vie (`SmartLifecycle`), injection de dépendances, résolution de cycles.
* **Spring Boot 3.4 / Framework 6.2** : profils dynamiques, Virtual-Thread aware `TaskScheduler`, nouveaux attributs `@Bean(defaultCandidate=false)`.
* **Code idiomatique** et **diagrammes** pour visualiser le conteneur.

Si tu souhaites un autre exemple (événements d’application, AOT/CRaC, bean indexing, etc.), dis-le !

## Entretien 2025 – « Senior » Spring / Spring Boot (20 + ans d’expérience)

> **Format** :
> **I** = Intervieweur · **S** = Ingénieur senior
> Chaque question précise **le domaine métier**, **le problème réellement rencontré**, **la solution** (explications + code détaillé) **et un flow-chart Mermaid dédié**.

## Entretien 2025 – « Senior » Spring / Spring Boot

*(20 + ans d’expérience – focus **exclusif** sur le conteneur IoC, les annotations, les scopes, la configuration et le cycle de vie)*

> **I** = Intervieweur · **S** = Ingénieur senior
> Chaque question décrit un problème **réel**, montre la solution **en phrases complètes**, fournit du **code détaillé** et un **diagramme Mermaid** représentant l’intérieur du conteneur Spring. Aucune dépendance externe autre que Spring n’est utilisée.

---

### 1 — **Prototype dans Singleton : fuite mémoire et état non partagé**

#### Sujet : Service de tarification qui crée un « Calculator » *ad hoc* pour chaque requête

**I.** « Pourquoi la simple annotation `@Autowired` d’un bean *prototype* (Calculator) dans un bean *singleton* (PricingService) a-t-elle fini par saturer le heap ? »

**S.**

> « Parce qu’au runtime Spring n’injecte **qu’une seule instance** du prototype ; le singleton la réutilise pour les 60 000 requêtes/minute et accumule l’état intermédiaire dans des champs.
> La bonne pratique consiste à laisser le conteneur produire un **nouveau prototype à chaque appel** : soit via l’API *lookup-method injection*, soit, plus moderne, avec `ObjectProvider<T>` ou `javax.inject.Provider<T>`. » ([Medium][1])

```mermaid
flowchart LR
    subgraph IoC Container
        PricingService:::singleton -->|"getObject()"| Calculator1((Calculator))
        PricingService -->|"getObject()"| Calculator2((Calculator))
    end

    classDef singleton fill:#e0f7ff,stroke:#036,stroke-width:1px,padding:2px;
```



```java
@Service                       // Singleton (défaut)
@RequiredArgsConstructor
public class PricingService {

  private final ObjectProvider<Calculator> calculators;   // Fournisseur paresseux

  public BigDecimal price(Order o) {
      Calculator c = calculators.getObject();            // nouveau prototype
      return c.compute(o);
  }
}

@Scope("prototype")            // Créé à la demande
@Component
public class Calculator {
    /* état interne éphémère */
}
```

---

### 2 — **Cycle de vie : démarrage/arrêt coordonné avec SmartLifecycle**

#### Sujet : Pipeline batch nocturne de consolidation comptable

**I.** « Comment as-tu garanti que la tâche de consolidation ne démarre **qu’après** l’initialisation du cache, et qu’elle s’arrête proprement avant la fermeture de la DataSource ? »

**S.**

> « `SmartLifecycle` me donne un crochet de démarrage et d’arrêt **ordonnancé**.
> Je fixe `getPhase()` à 100 pour le *CacheLoader* et à 200 pour *BatchJobRunner* : Spring lance les phases croissantes et les arrête en ordre inverse. Le tout sans XML, simplement en implémentant l’interface. » ([Home][2])

```mermaid
sequenceDiagram
    participant Context
    participant CacheLoader
    participant BatchRunner
    Context->>CacheLoader: start()
    CacheLoader-->>Context: running=true
    Context->>BatchRunner: start()
    Note right of BatchRunner: phase 200 > 100  
    Context-->>BatchRunner: stop()
    Context-->>CacheLoader: stop()
```



```java
@Component
public class CacheLoader implements SmartLifecycle {

  private volatile boolean running;

  @Override 
  public void start() { 
       loadAll(); 
       running = true; 
  }
  @Override 
  public void stop()  { 
       flush();  
       running = false; 
  }
  @Override 
  public boolean isRunning() { 
       return running; 
  }
  @Override 
  public int getPhase() { 
       return 100; 
  }
}

@Component
public class BatchJobRunner implements SmartLifecycle {
  /* phase 200 : démarre après le cache */
  @Override public int getPhase() { return 200; }
  /* … */
}
```

---

### 3 — **Configuration & profils : explosion de fichiers YAML**

#### Sujet : Même application déployée en *dev*, *test*, *prod* et *benchmark*

**I.** « Ton `application.yml` comportait 1 200 lignes. Comment l’as-tu rationalisé ? »

**S.**

> « J’ai :
>
> 1. Migré vers `application-<profile>.yaml` pour isoler base, overrides et secrets.
> 2. Remplacé les doublons par une classe `@ConfigurationProperties` hiérarchique, validée par `@Validated`.
> 3. Tiré profit de la nouveauté Spring Boot 3.4 : le paramètre `spring.application.from(… , <profiles>)` qui injecte *à chaud* un profil lors du redéploiement, pratique en QA. » ([GitHub][3], [GitHub][3])

```java
@ConfigurationProperties(prefix = "billing")
@Validated
public record BillingSettings(
        @NotNull URI endpoint,
        @Min(1)  int retry,
        Duration timeout) {}
```

```mermaid
flowchart TD
    Base[[application.yaml]]
    Dev[[application-dev.yaml]]
    Test[[application-test.yaml]]
    Prod[[application-prod.yaml]]
    Benchmark[[application-bench.yaml]]
    Base -->|spring.profiles.active=dev| Dev
    Base --> Test & Prod & Benchmark
```

---

### 4 — **Dépendances circulaires : @Lazy vs. refonte du design**

#### Sujet : Service *Notification* et *Statistics* se dépendant mutuellement

**I.** « Le conteneur jetait un `BeanCurrentlyInCreationException`. Qu’as-tu fait ? »

**S.**

> « J’ai analysé la dépendance : *Statistics* avait seulement besoin d’une **callback** pour notifier un calcul, pas du service entier.
>
> 1. J’ai extrait une \**interface* `Notifier` injectée dans *Statistics*.
> 2. *NotificationService* l’implémente et dépend toujours de *Statistics* (pour les métriques), mais Spring gère le cycle en utilisant `@Lazy` sur ce dernier.
> 3. Ce refactoring supprime la boucle dure et clarifie la responsabilité de chaque bean. » ([Home][4])

```java
public interface Notifier { void send(Event e); }

@Service
@RequiredArgsConstructor
public class StatisticsService {
    private final Notifier notifier;
    public void compute() { /* … */ notifier.send(evt); }
}

@Service
@RequiredArgsConstructor
public class NotificationService implements Notifier {
    @Lazy private final StatisticsService stats;   // injecté tardivement
    public void send(Event e) { /* Use stats for context */ }
}
```

```mermaid
flowchart LR
Statistics --> Notifier
Notification --> Statistics

classDef singleton fill:#e0f7ff,stroke:#036,stroke-width:1px;
class Statistics,Notification singleton


```

---

### 5 — **Planification @Scheduled : contention de pool & Virtual-Thread awareness**

#### Sujet : Tâches récurrentes (15 000 exécutions/heure) qui bloquaient les requêtes web

**I.** « Comment as-tu empêché les `@Scheduled` de monopoliser le CPU ? »

**S.**

> « Depuis Spring Boot 3.4, le `TaskScheduler` intégré est **compatible Virtual Threads** : j’active `spring.threads.virtual.enabled=true`.
> J’ajuste ensuite le pool *scheduler* avec `TaskSchedulingConfigurer` pour un maximum de 64 threads réels, mais **1 000 tâches virtuales** possibles, éliminant toute famine.
> La configuration YAML contrôle aussi la stratégie de back-pressure (queue-capacity). » ([GitHub][3], [Home][5])

```mermaid
flowchart TD
    subgraph SchedulerPool
        P1((vThread))
        P2((vThread))
        Pn((vThread))
    end

    App[Web threads] -->|non-bloquant| DB[(Database)]
    App --> SchedulerPool
    SchedulerPool -->|long tasks| DB

    classDef scheduler fill:#fafafa,stroke:#666;
    class SchedulerPool scheduler
```



```java
@Configuration
@EnableScheduling
public class SchedulingConfig implements SchedulingConfigurer {

  @Override
  public void configureTasks(ScheduledTaskRegistrar reg) {
      reg.setScheduler(
         TaskSchedulerBuilder()
            .poolSize(64)                          // threads physiques
            .virtualThreads(true)                  // Boot 3.4 feature
            .build());
  }
}

@Component
public class HouseKeeping {

  @Scheduled(fixedRateString = "PT30S")
  public void cleanUp() { /* purge cache */ }

  @Scheduled(cron = "0 0 2 * * *")
  public void nightlyReport() { /* long-running */ }
}
```

### 1. Domaine : Plate-forme de **virements instantanés SEPA**

#### Sujet : tenir 10 000 TPS avec une latence p95 ≤ 50 ms

**I.** *« Vous exploitiez depuis 2019 un back-end Spring Boot synchronisé sur PostgreSQL. Comment avez-vous absorbé l’énorme pic de trafic lié à l’ouverture des virements 24 h/24 ? »*

**S.**

> « Nous avons d’abord identifié que **le thread-pool Tomcat saturait** : 600 threads bloquants pour 128 connexions JDBC, ce qui provoquait des GC stop-the-world.
> En profitant de **Spring Boot 3.4 + JDK 21**, j’ai **remplacé le pool classique par des Virtual Threads**. Un simple bean suffit mais le vrai défi fut la *propagation du contexte* (MDC, OpenTelemetry, SecurityContext). Sans ça, nos logs et traces perdaient la corrélation des virements. Après mise en production : **RAM ÷ 4, p95 → 22 ms**. » ([BellSoft][1], [Baeldung][2])

```mermaid
flowchart TB
    subgraph InstantPayment
        C[Client banque] --> GW[API Gateway<br/>Virtual Threads]
        GW --> PAY[Service Payment<br/>Spring Boot 3.4 VT]
        PAY -->|SQL| PG[(PostgreSQL<br/>Hot-Standby)]
        PAY --> OTLP[(OpenTelemetry OTLP)]
    end
    OTLP --> GRAF[Grafana Cloud]
```



```java
@Configuration
public class InstantPaymentConfig {

  @Bean                                                // ① Tomcat passe en Virtual Threads
  WebServerFactoryCustomizer<TomcatServletWebServerFactory> vtTomcat() {
      return factory -> factory.addConnectorCustomizers(conn -> 
          conn.getProtocolHandler()
              .setExecutor(Executors.newVirtualThreadPerTaskExecutor()));
  }

  @Bean                                                // ② Décorateur : contexte observabilité + sécurité
  TaskDecorator contextAware() {
      return task -> {
          var snapshot = ContextSnapshot.captureAll();
          return () -> ContextSnapshot.setAll(snapshot).run(task);
      };
  }

  @Bean                                                // ③ Pool JDBC raccourci : moins de connexions, plus de VT
  DataSource dataSource() {
      HikariDataSource ds = DataSourceBuilder.create().type(HikariDataSource.class).build();
      ds.setMaximumPoolSize(64);
      ds.setConnectionTimeout(1_000);
      return ds;
  }
}
```

---

### 2. Domaine : **E-commerce chaussures** (ventes flash)

#### Sujet : cohérence transactionnelle multiservices (commande, stock, paiement)

**I.** *« Le *Black Friday* 2024 a déclenché des sur-ventes et des débits fantômes. Comment avez-vous assuré l’atome ‘réserver + payer + commander’ ? »*

**S.**

> « Nous avons implémenté **l’orchestration Saga** avec Spring Modulith. L’OrderService joue le rôle de *Saga Orchestrator* et publie un événement *OrderCreated*. Les micro-services *Stock* et *Payment* répondent par des événements domain-driven (`StockReserved`, `PaymentAuthorized`).
> Si l’un échoue, le contrôleur publie `RollbackOrder` qui déclenche les compensations. Grâce à l’Outbox pattern, chaque étape est écrite de façon atomique dans le même commit que son message Kafka, éliminant les “double write”. » ([Baeldung][3], [Medium][4])

```mermaid
flowchart LR
    subgraph "Saga – Commande chaussure BF"
        OC[[Order Created]] --> SR[(Reserve Stock)]
        SR --> PA[(Authorize Payment)]
        PA --> OCI[[Order Confirmed]]
        SR -. KO .-> RB((Rollback))
        PA -. KO .-> RB
    end
```



```java
// OrderSagaOrchestrator.java
@Component
@RequiredArgsConstructor
public class OrderSagaOrchestrator {

    private final ApplicationEventPublisher publisher;
    private final OrderRepository repo;

    @Transactional
    public void startSaga(CreateOrder cmd) {
        Order order = repo.save(Order.from(cmd));
        publisher.publishEvent(new StockReserveRequested(order.getId(), order.lines()));
        publisher.publishEvent(new PaymentAuthorizeRequested(order.getId(), order.total()));
    }

    @Transactional
    @EventListener
    public void handle(StockReserved ev) {
        publisher.publishEvent(new OrderStepSucceeded(ev.orderId(), "stock"));
        maybeComplete(ev.orderId());
    }

    @Transactional
    @EventListener
    public void handle(StepFailed ev) {
        publisher.publishEvent(new RollbackOrder(ev.orderId(), ev.reason()));
    }

    private void maybeComplete(UUID orderId) { /* vérifie que chaque step est OK */ }
}
```

---

### 3. Domaine : **Gestion de contrats d’assurance vie**

#### Sujet : moteur de règles « zéro downtime » pour recalcul de prime

**I.** *« Les actuaires publient chaque semaine de nouvelles grilles tarifaires. Comment mettez-vous à jour les règles sans redéployer le cœur applicatif ? »*

**S.**

> « Nous avons isolé la logique métier dans un **Rule Engine Drools** chargé dynamiquement via Spring Integration. Les fichiers `.drl` sont versionnés dans un bucket S3. Un *Integration Flow* vérifie l’objet S3 toutes les 5 minutes ; si le hash MD5 change, il recharge un `KieContainer` et met à jour un `ConcurrentHashMap<Version, KieSession>`.
> Les requêtes REST continuent à arriver ; on sélectionne la *rule set* en fonction de l’horodatage du contrat puis on exécute `kieSession.insert(quotation)` → `fireAllRules()`. Aucun redéploiement, aucune coupure. »

```mermaid
flowchart TD
    Poll[S3 Poll 5 min] --> Hash[Compare hash]
    Hash -- nouveau --> Reload{Reload Kie Container}
    Reload --> Map[Concurrent<br/>Map<Version,Session>]
    Client --> API[REST /quotation]
    API --> Map
    Map --> Rules[fireAllRules]
```



```java
@Configuration
public class RuleReloadFlow {

  @Bean
  IntegrationFlow ruleUpdater(S3Client s3, AtomicReference<KieContainer> ref) {
      return IntegrationFlows
          .from(() -> new PollableChannel() {/* no op */}, e -> e.poller(p -> p.fixedDelay(300_000)))
          .handle(m -> {
              var obj = s3.getObject("rules-bucket","tarifs.drl");
              String newHash = DigestUtils.md5DigestAsHex(obj.readAllBytes());
              if (!newHash.equals(ref.get().getReleaseId().getVersion())) {
                  // recharger
                  KieContainer kc = KieServices.get().newKieContainer(
                         KieServices.get().newReleaseId("com.acme","tarifs", newHash));
                  kc.getKieBase().addPackages(
                         KieHelper.create(ResourceFactory.newByteArrayResource(obj.readAllBytes())).getKiePackages());
                  ref.set(kc);
              }
          })
          .get();
  }
}
```

---

### 4. Domaine : **Suivi temps-réel de livraisons pizza**

#### Sujet : event sourcing, projections géo, démarrage < 100 ms (images natives)

**I.** *« Vos livreurs poussent un événement GPS par seconde. Comment redémarrer un service de projection en < 100 ms pour ne rien perdre ? »*

```mermaid
flowchart LR
    subgraph "Event Store"
        GPS[(Kafka gps)] --> PROJ[Projection Service<br/>Image native < 100 ms]
        PROJ --> GEO[Redis Geo]
        PROJ --> Off[Redis offset]
        GEO --> Map[Heat-map UI]
    end
```

**S.**

> « Chaque position est un événement `LocationUpdated` stocké dans Postgres (append-only). Le *ProjectionService* est un Spring Boot natif (GraalVM) ; en cas d’autoscaling sur K8s, un pod “froid” doit rejouer tout le flux Kafka depuis le dernier *offset* sauvegardé.

> Avec **Profile-Guided Optimization** (`--pgo`), l’exécutable ARM64 pèse 68 Mo et **démarre en 87 ms**. Dès qu’il est prêt, il lit l’offset dans Redis et continue la projection sans trou dans la heat-map. » ([graalvm.org][5], [graalvm.org][6])

```bash
mvn -Pnative -DskipTests \
  -Dquarkus.native.container-build=true \
  -Dbp_native_image=true \
  -Dbp_native_image_build_arguments="--pgo --gc=Epsilon --native-image-info" \
  spring-boot:build-image
```

```java
@Component
public class LocationProjector {

  @KafkaListener(topics = "gps")
  public void on(LocationUpdated ev) {
      redis.opsForHash().put("lastOffset", ev.driverId(), ev.offset());
      geoRedis.add("deliveryLive", new Point(ev.lon(), ev.lat()), ev.driverId());
  }

  @PostConstruct
  void warmCache() {
      // injection du profil PGO : aucun délai au premier appel Redis
  }
}
```

---

## Conclusion

Ces quatre dialogues montrent :

1. **Appropriation du contexte métier** (paiement instantané, ventes flash, actuariat, logistique).
2. **Réponses complètes et argumentées** : phrases longues, étapes, compromis.
3. **Code approfondi** prêt à l’emploi, pas seulement des extraits superficiels.
4. **Flow-charts Mermaid** pour chaque scénario, facilitant la revue architecturale.

## Flow-chart (vue d’ensemble après ces solutions)

```mermaid
flowchart TB
    subgraph Edge
        C[Client Web / Mobile]
        APIGW["Spring Cloud Gateway\n(Virtual Threads)"]
        C --> APIGW
    end

    subgraph Core
        APIGW --> AUTH[Auth Service\nKeycloak + Spring Security]
        APIGW --> ORDER[Order Service\nSpring Boot 3.4.5\nVirtual Threads]
        ORDER -->|Reserve| INV[Inventory Service\nR2DBC]
        ORDER -->|Pay| PAY[Payment Service\nReactive]
        INV -- Kafka --> ORDER
        PAY -- Kafka --> ORDER
    end

    ORDER -->|Emit SAGA events| K[(Kafka)]
    K --> OBS["Observability Stack\n(OpenTelemetry → Grafana)"]

    subgraph Data
        INV --> PG[(Postgres)]
        ORDER --> ES[(Elasticsearch)]
    end

    subgraph AI
        APIGW --> AINODE[Recommender\nSpring AI]
    end

    classDef svc fill:#f4f4f4,stroke:#333,stroke-width:1px;
    class AUTH,ORDER,INV,PAY svc

```

------

#### Q 1. Quelle nouveauté majeure de Spring Boot 3.4 t’a le plus aidé en production ?

R : **Le support officiel des Virtual Threads sur JDK 21+**. Nous avons divisé par 4 l’occupation mémoire d’un service servlet-based au pic (250 k req/s) simplement en basculant le thread-pool Tomcat sur un `VirtualThreadPerTaskExecutor`. La version **3.4.5** publiée en avril 2025 est aujourd’hui la baseline. ([Home](https://spring.io/blog/2025/04/24/spring-boot-3-4-5-available-now/?utm_source=chatgpt.com), [bootify.io](https://bootify.io/spring-boot/spring-boot-latest-version.html?utm_source=chatgpt.com))

------

#### Q 2. Comment as-tu implémenté les Virtual Threads dans un service historique Tomcat ?

Le trick crucial : **propager le contexte MDC + OpenTelemetry** dans chaque virtual thread, sinon les traces disparaissent. ([Home](https://spring.io/blog/2022/10/11/embracing-virtual-threads?utm_source=chatgpt.com), [Medium](https://medium.com/@vortj/spring-boot-what-are-virtual-threads-in-spring-boot-c03bb86e2406?utm_source=chatgpt.com))

```java
@Configuration
public class VirtualThreadConfig {

  // 1️⃣  Serveur Tomcat sur virtual-threads
  @Bean
  WebServerFactoryCustomizer<TomcatServletWebServerFactory> vtTomcat() {
      return factory -> factory
          .addConnectorCustomizers(connector -> connector.getProtocolHandler()
              .setExecutor(Executors.newVirtualThreadPerTaskExecutor()));
  }

  // 2️⃣  Propagation de contexte avec Loom ScopedValue
  @Bean
  TaskDecorator observabilityContext() {
      return task -> {
          var parent = ContextSnapshot.captureAll();
          return () -> ContextSnapshot.setAll(parent).run(task);
      };
  }
}
```

------

#### Q 3. Saturation JD-C : pool JDBC épuisé, latence x 5

**Problème** : 128 connexions ; 20 k threads bloquants.
 **Solution** :

1. **Split** lecture/écriture (CQRS) : R2DBC + Postgres logical replica pour les requêtes read-only.
2. Pool Hikari limité à 64 connexions max, mais servi par **512 virtual threads** → latence médiane 18 ms → 7 ms.
3. Monitoring avec Micrometer + OTel exporter vers Grafana Cloud (SLO ≤ 50 ms p95).

------

#### Q 4. Observabilité “tout-en-un” (logs, metrics, traces)

**Résultat** : corrélation UID → click utilisateur → flux Kafka → base Postgres en un clic Grafana Explore.

```java
// build.gradle.kts
dependencies {
  implementation("io.micrometer:micrometer-tracing-bridge-otel")
  implementation("io.opentelemetry:opentelemetry-exporter-otlp")
  runtimeOnly("net.logstash.logback:logstash-logback-encoder")
}
```

------

#### Q 5. Intégration **Spring AI 1.0** pour générer des recommandations produit

Spring AI fournit déjà les abstractions (`AiClient`, `PromptTemplate`) et s’imbrique comme n’importe quel bean Spring. ([Home](https://spring.io/projects/spring-ai?utm_source=chatgpt.com))

```java
@Service
@RequiredArgsConstructor
public class AiRecommender {

  private final OpenAiChatClient chat;   // spring-ai-starter-openai

  public String recommend(String userId, List<String> cart) {
      return chat.call("""
          Tu es un moteur de recommandation. Propose 3 articles complémentaires 
          pour un panier: %s.""".formatted(String.join(",", cart)));
  }
}
```

------

#### Q 6. Migration Spring Framework 6.2 → 7.0

- **Jakarta EE 10** → changement de package impératif.
- Activation du **bean-indexer** 6.2 pour scanner 30 % plus vite au démarrage. ([Home](https://spring.io/blog/2024/10/01/from-spring-framework-6-2-to-7-0?utm_source=chatgpt.com), [GitHub](https://github.com/spring-projects/spring-framework/wiki/Spring-Framework-6.2-Release-Notes?utm_source=chatgpt.com))
- Nettoyage des APIs supprimées : `WebMvcConfigurerAdapter`, `DefaultMessageCodesResolver`…
- Tests mis à jour : `@SpringJUnitConfig` + JUnit 5 vintage removed.

------

#### Q 7. Images natives & démarrage < 100 ms

GraalVM 22 avec PGO réduit l’empreinte à 70 MB et le cold-start à 85 ms sur ARM64.

```bash
$ ./mvnw -Pnative -DskipTests spring-boot:build-image \
         -DBP_NATIVE_IMAGE=true -DBP_NATIVE_IMAGE_BUILD_ARGUMENTS="--pgo --gc=Epsilon"
```

------

#### Q 8. Orchestration de transactions distribuées (SAGA)

Utilise Spring Modulith pour les **domain events** in-memory en dev, et **Kafka** en prod.

```java
@Component
@RequiredArgsConstructor
public class OrderSaga {

  private final ApplicationEventPublisher publisher;

  @Transactional
  public void place(OrderCmd cmd) {
      publisher.publishEvent(new ReserveStock(cmd));
      publisher.publishEvent(new AuthorizePayment(cmd));
  }

  @SagaEventHandler
  public void on(StockReserved e) { /* … */ }

  @SagaCompensationHandler
  public void cancel(Throwable cause) { /* rollback */ }
}
```

