// generate-diagrams.mjs
// Creates hand-drawn style diagrams for Ethiopia DS Workshop slides
// Run with: node scripts/generate-diagrams.mjs

import { createCanvas } from 'canvas';
import rough from 'roughjs';
import fs from 'fs';
import path from 'path';

// Configuration
const ROUGHNESS = 1.2; // Slight hand-drawn feel

// Color palette - workshop theme
const PALETTE = {
  bg: '#FFFFFF',
  stroke: '#2c3e50',
  text: '#2c3e50',
  red: '#e74c3c',
  blue: '#3498db',
  green: '#27ae60',
  purple: '#9b59b6',
  gray: '#95a5a6'
};

// Output directory
const OUTPUT_DIR = path.join(import.meta.dirname, '..', 'images');

// ============================================================
// Diagram 1: Data Science Venn Diagram
// ============================================================
function createDataScienceVenn() {
  const WIDTH = 800;
  const HEIGHT = 600;

  const canvas = createCanvas(WIDTH, HEIGHT);
  const ctx = canvas.getContext('2d');
  const rc = rough.canvas(canvas);

  // White background
  ctx.fillStyle = PALETTE.bg;
  ctx.fillRect(0, 0, WIDTH, HEIGHT);

  // Circle positions (overlapping venn)
  const centerX = WIDTH / 2;
  const centerY = HEIGHT / 2 - 30;
  const radius = 140;
  const offset = 100; // How far apart the circle centers are

  // Three overlapping circles
  const circles = [
    { x: centerX, y: centerY - offset, color: PALETTE.red, label: 'Domain Knowledge', sublabel: 'Health Systems\nSupply Chains\nPolicy Context' },
    { x: centerX - offset * 0.866, y: centerY + offset * 0.5, color: PALETTE.blue, label: 'Statistics & Math', sublabel: 'Probability\nInference\nModeling' },
    { x: centerX + offset * 0.866, y: centerY + offset * 0.5, color: PALETTE.green, label: 'Computing', sublabel: 'Programming\nData Management\nVisualization' }
  ];

  // Draw circles with transparency effect (just outlines for cleaner look)
  circles.forEach(c => {
    rc.circle(c.x, c.y, radius * 2, {
      stroke: c.color,
      strokeWidth: 3,
      fill: c.color + '20', // 20% opacity
      fillStyle: 'solid',
      roughness: ROUGHNESS
    });
  });

  // Center label: "Data Science"
  ctx.fillStyle = PALETTE.purple;
  ctx.font = 'bold 24px Arial';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText('DATA SCIENCE', centerX, centerY);

  // Circle labels - positioned outside
  ctx.font = 'bold 16px Arial';
  ctx.fillStyle = PALETTE.text;

  // Domain Knowledge (top)
  ctx.fillText('Domain Knowledge', centerX, centerY - offset - radius - 40);
  ctx.font = '13px Arial';
  ctx.fillStyle = '#666666';
  ctx.fillText('Health Systems • Supply Chains • Policy', centerX, centerY - offset - radius - 20);

  // Statistics (bottom-left)
  ctx.font = 'bold 16px Arial';
  ctx.fillStyle = PALETTE.text;
  ctx.fillText('Statistics & Math', centerX - offset * 0.866 - 60, centerY + offset * 0.5 + radius + 30);
  ctx.font = '13px Arial';
  ctx.fillStyle = '#666666';
  ctx.fillText('Probability • Inference • Modeling', centerX - offset * 0.866 - 60, centerY + offset * 0.5 + radius + 50);

  // Computing (bottom-right)
  ctx.font = 'bold 16px Arial';
  ctx.fillStyle = PALETTE.text;
  ctx.fillText('Computing', centerX + offset * 0.866 + 60, centerY + offset * 0.5 + radius + 30);
  ctx.font = '13px Arial';
  ctx.fillStyle = '#666666';
  ctx.fillText('Programming • Data • Visualization', centerX + offset * 0.866 + 60, centerY + offset * 0.5 + radius + 50);

  // Save
  const buffer = canvas.toBuffer('image/png');
  fs.writeFileSync(path.join(OUTPUT_DIR, 'data-science-venn.png'), buffer);
  console.log('✅ Created: data-science-venn.png');
}

// ============================================================
// Diagram 2: Workshop Pipeline Flowchart
// ============================================================
function createWorkshopPipeline() {
  const WIDTH = 900;
  const HEIGHT = 400;

  const canvas = createCanvas(WIDTH, HEIGHT);
  const ctx = canvas.getContext('2d');
  const rc = rough.canvas(canvas);

  // White background
  ctx.fillStyle = PALETTE.bg;
  ctx.fillRect(0, 0, WIDTH, HEIGHT);

  // Box dimensions
  const boxWidth = 160;
  const boxHeight = 120;
  const gap = 50;
  const startX = 60;
  const startY = (HEIGHT - boxHeight) / 2;

  // Four boxes
  const boxes = [
    {
      label: 'Historical Data',
      sublabel: 'Facility reports\nInventory levels\nDemand patterns',
      color: PALETTE.gray
    },
    {
      label: 'ML Models',
      sublabel: 'Demand forecasting\nRisk prediction\nDays 2-3',
      color: PALETTE.blue
    },
    {
      label: 'Agent-Based Model',
      sublabel: 'Supply chain simulation\nPolicy scenarios\nDays 3-4',
      color: PALETTE.red
    },
    {
      label: 'Policy Insights',
      sublabel: 'Optimal allocation\nIntervention design\nEvidence for decisions',
      color: PALETTE.green
    }
  ];

  boxes.forEach((box, i) => {
    const x = startX + i * (boxWidth + gap);

    // Draw rounded rectangle
    rc.rectangle(x, startY, boxWidth, boxHeight, {
      fill: box.color,
      fillStyle: 'solid',
      stroke: box.color,
      strokeWidth: 2,
      roughness: ROUGHNESS
    });

    // Label
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 14px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText(box.label, x + boxWidth / 2, startY + 15);

    // Sublabel (multiline)
    ctx.font = '11px Arial';
    const lines = box.sublabel.split('\n');
    lines.forEach((line, j) => {
      ctx.fillText(line, x + boxWidth / 2, startY + 40 + j * 16);
    });

    // Arrow to next box (if not last)
    if (i < boxes.length - 1) {
      const arrowStartX = x + boxWidth + 5;
      const arrowEndX = x + boxWidth + gap - 5;
      const arrowY = startY + boxHeight / 2;

      rc.line(arrowStartX, arrowY, arrowEndX, arrowY, {
        stroke: PALETTE.stroke,
        strokeWidth: 2,
        roughness: ROUGHNESS * 0.8
      });

      // Arrowhead
      rc.line(arrowEndX - 10, arrowY - 8, arrowEndX, arrowY, {
        stroke: PALETTE.stroke,
        strokeWidth: 2,
        roughness: ROUGHNESS * 0.5
      });
      rc.line(arrowEndX - 10, arrowY + 8, arrowEndX, arrowY, {
        stroke: PALETTE.stroke,
        strokeWidth: 2,
        roughness: ROUGHNESS * 0.5
      });
    }
  });

  // Title at top
  ctx.fillStyle = PALETTE.text;
  ctx.font = 'bold 18px Arial';
  ctx.textAlign = 'center';
  ctx.fillText('Workshop Pipeline: From Data to Policy', WIDTH / 2, 30);

  // Save
  const buffer = canvas.toBuffer('image/png');
  fs.writeFileSync(path.join(OUTPUT_DIR, 'workshop-pipeline.png'), buffer);
  console.log('✅ Created: workshop-pipeline.png');
}

// ============================================================
// Run all diagram generators
// ============================================================
console.log('Generating hand-drawn diagrams for Ethiopia DS Workshop...\n');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

createDataScienceVenn();
createWorkshopPipeline();

console.log('\n✅ All diagrams created in:', OUTPUT_DIR);
