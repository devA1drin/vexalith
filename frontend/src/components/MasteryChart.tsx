"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Cell,
} from "recharts";
import type { DomainProgress } from "@/lib/api";

const COLORS = ["#e8a838", "#6e9bc1", "#7ec8a3", "#c98bdb", "#f07178"];

export function MasteryChart({ domains }: { domains: DomainProgress[] }) {
  const data = domains.map((d) => ({
    name: d.domain_name.replace(" ", "\n"),
    short: d.domain_slug.split("_")[0],
    mastery: Math.round(d.mastery * 100),
    attempts: d.attempts,
  }));

  return (
    <div className="h-72 w-full rounded-xl border border-ink-700 bg-ink-900/50 p-4">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 24 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#314f70" vertical={false} />
          <XAxis
            dataKey="short"
            tick={{ fill: "#a0bfd9", fontSize: 12 }}
            axisLine={{ stroke: "#314f70" }}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fill: "#a0bfd9", fontSize: 12 }}
            axisLine={{ stroke: "#314f70" }}
            unit="%"
          />
          <Tooltip
            contentStyle={{
              background: "#1a2534",
              border: "1px solid #314f70",
              borderRadius: 8,
              color: "#e8eef6",
            }}
            formatter={(value: number, _name, props) => [
              `${value}% (${props.payload.attempts} attempts)`,
              props.payload.name.replace("\n", " "),
            ]}
          />
          <Bar dataKey="mastery" radius={[6, 6, 0, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
