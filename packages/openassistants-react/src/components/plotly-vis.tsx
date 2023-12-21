import React from 'react';
import { useEffect } from 'react';

interface RenderVisMessageProps {
  id: string;
  data: any;
  layout: any;
}

export const RenderVisMessage = ({
  id,
  data,
  layout,
}: RenderVisMessageProps) => {
  const Plotly =
    typeof window !== 'undefined' ? require('plotly.js-dist-min') : null;
  useEffect(() => {
    if (!data || !layout) {
      return;
    }
    const graphDiv = document.getElementById(id);
    if (!graphDiv) {
      console.log(`could not find graphDiv for id ${id}`);
      return;
    }
    const responsiveLayout = {
      ...layout,
      autosize: true,
    };
    Plotly.newPlot(graphDiv, data, responsiveLayout);
    window.onresize = () => Plotly.Plots.resize(graphDiv);
  }, [data, layout]);

  return <div className="overflow-x-auto" id={id}></div>;
};
