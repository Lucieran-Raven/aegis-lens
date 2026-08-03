import { useEffect, useRef } from 'react';
import * as d3 from 'd3';

export interface ChartData {
  label: string;
  value: number;
  color?: string;
}

export interface TimeSeriesData {
  timestamp: Date;
  value: number;
}

export function useD3Chart(
  renderChart: (svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, data: ChartData[]) => void,
  data: ChartData[]
) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data.length) return;

    const svg = d3.select(svgRef.current);
    
    // Clear previous content
    svg.selectAll('*').remove();

    renderChart(svg, data);
  }, [data, renderChart]);

  return svgRef;
}

export function useD3TimeSeries(
  renderChart: (svg: d3.Selection<SVGSVGElement, unknown, null, undefined>, data: TimeSeriesData[]) => void,
  data: TimeSeriesData[]
) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data.length) return;

    const svg = d3.select(svgRef.current);
    
    // Clear previous content
    svg.selectAll('*').remove();

    renderChart(svg, data);
  }, [data, renderChart]);

  return svgRef;
}

export function createPieChart(
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  data: ChartData[],
  width: number = 300,
  height: number = 300
) {
  const radius = Math.min(width, height) / 2;
  
  svg.attr('width', width).attr('height', height);
  
  const g = svg
    .append('g')
    .attr('transform', `translate(${width / 2},${height / 2})`);

  const pie = d3.pie<ChartData>().value((d: ChartData) => d.value);
  const arc = d3.arc<d3.PieArcDatum<ChartData>>().innerRadius(0).outerRadius(radius);
  const color = d3.scaleOrdinal(d3.schemeCategory10);

  const arcs = g.selectAll('arc')
    .data(pie(data))
    .enter()
    .append('g');

  arcs.append('path')
    .attr('d', arc)
    .attr('fill', (d: d3.PieArcDatum<ChartData>) => d.data.color || color(d.data.label.toString()))
    .attr('stroke', 'white')
    .attr('stroke-width', 2);

  arcs.append('text')
    .attr('transform', (d: d3.PieArcDatum<ChartData>) => `translate(${arc.centroid(d)})`)
    .attr('text-anchor', 'middle')
    .attr('font-size', '12px')
    .text((d: d3.PieArcDatum<ChartData>) => `${d.data.label} (${d.data.value})`);
}

export function createLineChart(
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  data: TimeSeriesData[],
  width: number = 600,
  height: number = 300
) {
  const margin = { top: 20, right: 30, bottom: 40, left: 50 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  svg.attr('width', width).attr('height', height);

  const g = svg
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleTime()
    .domain(d3.extent(data, (d: TimeSeriesData) => d.timestamp) as [Date, Date])
    .range([0, innerWidth]);

  const y = d3.scaleLinear()
    .domain([0, d3.max(data, (d: TimeSeriesData) => d.value) || 100])
    .range([innerHeight, 0]);

  const line = d3.line<TimeSeriesData>()
    .x((d: TimeSeriesData) => x(d.timestamp))
    .y((d: TimeSeriesData) => y(d.value))
    .curve(d3.curveMonotoneX);

  // X axis
  g.append('g')
    .attr('transform', `translate(0,${innerHeight})`)
    .call(d3.axisBottom(x).ticks(5))
    .selectAll('text')
    .attr('transform', 'rotate(-45)')
    .style('text-anchor', 'end');

  // Y axis
  g.append('g')
    .call(d3.axisLeft(y));

  // Grid lines
  g.append('g')
    .attr('class', 'grid')
    .call(d3.axisLeft(y)
      .tickSize(-innerWidth)
      .tickFormat('' as any)
    )
    .selectAll('line')
    .attr('stroke', '#e0e0e0')
    .attr('stroke-dasharray', '3,3');

  // Line path
  g.append('path')
    .datum(data)
    .attr('fill', 'none')
    .attr('stroke', '#0ea5e9')
    .attr('stroke-width', 2)
    .attr('d', line);

  // Dots
  g.selectAll('dot')
    .data(data)
    .enter()
    .append('circle')
    .attr('cx', (d: TimeSeriesData) => x(d.timestamp))
    .attr('cy', (d: TimeSeriesData) => y(d.value))
    .attr('r', 4)
    .attr('fill', '#0ea5e9');
}

export function createBarChart(
  svg: d3.Selection<SVGSVGElement, unknown, null, undefined>,
  data: ChartData[],
  width: number = 600,
  height: number = 300
) {
  const margin = { top: 20, right: 30, bottom: 40, left: 50 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  svg.attr('width', width).attr('height', height);

  const g = svg
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  const x = d3.scaleBand()
    .domain(data.map((d) => d.label))
    .range([0, innerWidth])
    .padding(0.3);

  const y = d3.scaleLinear()
    .domain([0, d3.max(data, (d: ChartData) => d.value) || 100])
    .range([innerHeight, 0]);

  // X axis
  g.append('g')
    .attr('transform', `translate(0,${innerHeight})`)
    .call(d3.axisBottom(x))
    .selectAll('text')
    .attr('transform', 'rotate(-45)')
    .style('text-anchor', 'end');

  // Y axis
  g.append('g')
    .call(d3.axisLeft(y));

  // Bars
  g.selectAll('rect')
    .data(data)
    .enter()
    .append('rect')
    .attr('x', (d: ChartData) => x(d.label) || 0)
    .attr('y', (d: ChartData) => y(d.value))
    .attr('width', x.bandwidth())
    .attr('height', (d: ChartData) => innerHeight - y(d.value))
    .attr('fill', (d: ChartData) => d.color || '#0ea5e9')
    .attr('rx', 4);
}
