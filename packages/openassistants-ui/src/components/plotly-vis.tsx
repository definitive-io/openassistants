import React from "react";
import { useEffect } from "react";


interface RenderVisMessageProps {
  id: string;
  data: any;
  layout: any;
}

export const RenderVisMessage = ({id, data, layout}: RenderVisMessageProps) => {
    console.log(`RenderVisMessage: id=${id}, data=${data}, layout=${layout}`);
    const Plotly =
      typeof window !== 'undefined' ? require('plotly.js-dist-min') : null;
    useEffect(() => {
      const graphDiv = document.getElementById(id);
      if (!graphDiv) {
        console.log(`could not find graphDiv for id ${id}`);
        return;
      }
      Plotly.newPlot(graphDiv, data, layout);
      const responsiveLayout = {
        ...layout,
        autosize: true,
      };
      window.onresize = () => Plotly.Plots.resize(graphDiv);
    }, [data, layout]);

    if (data && layout) {
      return <div className="overflow-x-auto" id={id}></div>;
    }
    return <div></div>;
  };
