import clsx from "clsx";
import Heading from "@theme/Heading";
import styles from "./styles.module.css";

const FeatureList = [
  {
    title: "Streamlined Function Deployment",
    Svg: require("@site/static/img/streamlined_functions_light.svg").default,
    description: (
      <>
        OpenAssistants simplifies the integration of AI into your workflows.
        Define your Python functions, and our framework does the rest,
        seamlessly embedding advanced AI capabilities into your projects.
      </>
    ),
  },
  {
    title: "Focus on Innovation, Not Infrastructure",
    Svg: require("@site/static/img/innovation_light.svg").default,
    description: (
      <>
        OpenAssistants empowers you to concentrate on creating groundbreaking AI
        functions, while it handles the intricate technicalities. Immerse
        yourself in developing your project's core capabilities, and let the
        framework manage the rest.
      </>
    ),
  },
  {
    title: "Python-Powered Versatility",
    Svg: require("@site/static/img/python_versatility_light.svg").default,
    description: (
      <>
        Leveraging Python's robustness, OpenAssistants offers a flexible and
        powerful backend, adaptable to various tasks and workflows, from
        database queries to automated emails, all within a consistent and
        reliable framework.
      </>
    ),
  },
];

function Feature({ Svg, title, description }) {
  return (
    <div className={clsx("col col--4")}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
