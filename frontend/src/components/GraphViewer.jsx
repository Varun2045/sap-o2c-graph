import React, { useRef, useEffect, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

const GraphViewer = ({ data, onNodeClick, onNodeHover }) => {
  const graphRef = useRef();
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [highlightLinks, setHighlightLinks] = useState(new Set());
  const [hoverNode, setHoverNode] = useState(null);

  const handleNodeHover = (node) => {
    setHoverNode(node);
    if (onNodeHover) {
      onNodeHover(node);
    }
    
    if (!node) {
      setHighlightNodes(new Set());
      setHighlightLinks(new Set());
      return;
    }

    const neighbors = new Set();
    const linkIds = new Set();
    
    if (data && data.links) {
      data.links.forEach(link => {
        if (link.source.id === node.id || link.source === node.id) {
          neighbors.add(link.target.id || link.target);
          linkIds.add(link.id);
        } else if (link.target.id === node.id || link.target === node.id) {
          neighbors.add(link.source.id || link.source);
          linkIds.add(link.id);
        }
      });
    }

    setHighlightNodes(neighbors);
    setHighlightLinks(linkIds);
  };

  const handleNodeClick = (node) => {
    if (onNodeClick) {
      onNodeClick(node);
    }
  };

  const getNodeColor = (nodeType) => {
    switch (nodeType) {
      case 'Customer':
        return '#FF6B6B';
      case 'SalesOrder':
        return '#4ECDC4';
      case 'BillingDocument':
        return '#45B7D1';
      case 'Delivery':
        return '#96CEB4';
      case 'JournalEntry':
        return '#FFEAA7';
      default:
        return '#999';
    }
  };

  const getNodeSize = (nodeType) => {
    switch (nodeType) {
      case 'Customer':
        return 8;
      case 'SalesOrder':
        return 5;
      case 'BillingDocument':
        return 6;
      case 'Delivery':
        return 4;
      case 'JournalEntry':
        return 4;
      default:
        return 4;
    }
  };

  const paintNode = (node, ctx) => {
    const isHighlighted = highlightNodes.has(node.id) || hoverNode?.id === node.id;
    const color = getNodeColor(node.type);
    const size = getNodeSize(node.type);
    const radius = isHighlighted ? size * 1.5 : size;

    // Draw node circle
    ctx.beginPath();
    ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
    ctx.fillStyle = isHighlighted ? '#FF0000' : color;
    ctx.fill();
    
    // Add border for highlighted nodes
    if (isHighlighted) {
      ctx.strokeStyle = '#FFFFFF';
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    // Draw label underneath node
    ctx.font = `${Math.max(10, size * 2)}px Arial`;
    ctx.fillStyle = '#FFFFFF';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    
    // Add text shadow for better readability
    ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
    ctx.shadowBlur = 3;
    ctx.shadowOffsetX = 1;
    ctx.shadowOffsetY = 1;
    
    // Truncate label if too long
    const maxLabelLength = 15;
    const label = node.label.length > maxLabelLength 
      ? node.label.substring(0, maxLabelLength) + '...' 
      : node.label;
    
    ctx.fillText(label, node.x, node.y + radius + 3);
    
    // Reset shadow
    ctx.shadowColor = 'transparent';
    ctx.shadowBlur = 0;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = 0;
  };

  const paintLink = (link, ctx) => {
    const isHighlighted = highlightLinks.has(link.id);
    
    ctx.beginPath();
    ctx.moveTo(link.source.x, link.source.y);
    ctx.lineTo(link.target.x, link.target.y);
    
    if (isHighlighted) {
      ctx.strokeStyle = '#ff0000';
      ctx.lineWidth = 2;
    } else {
      ctx.strokeStyle = '#999';
      ctx.lineWidth = 1;
    }
    
    ctx.stroke();
  };

  if (!data || !data.nodes || !data.links) {
    return (
      <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <p>No graph data available</p>
      </div>
    );
  }

  return (
    <div style={{ width: '100%', height: '100%' }}>
      <ForceGraph2D
        ref={graphRef}
        graphData={data}
        nodeLabel="label"
        nodeCanvasObject={paintNode}
        linkCanvasObject={paintLink}
        onNodeClick={handleNodeClick}
        onNodeHover={handleNodeHover}
        enableNodeDrag={true}
        enableZoomInteraction={true}
        enablePanInteraction={true}
        backgroundColor="#0d1117"
        cooldownTicks={100}
        d3AlphaDecay={0.02}
        d3VelocityDecay={0.3}
        nodeVal={(node) => getNodeSize(node.type)}
        nodeColor={(node) => getNodeColor(node.type)}
      />
      
      {hoverNode && (
        <div style={{
          position: 'absolute',
          top: '10px',
          right: '10px',
          background: 'rgba(255, 255, 255, 0.9)',
          padding: '10px',
          border: '1px solid #ccc',
          borderRadius: '5px',
          maxWidth: '300px'
        }}>
          <h4>{hoverNode.label}</h4>
          <p><strong>Type:</strong> {hoverNode.type}</p>
          {hoverNode.data && Object.entries(hoverNode.data).slice(0, 3).map(([key, value]) => (
            <p key={key}><strong>{key}:</strong> {value}</p>
          ))}
        </div>
      )}
    </div>
  );
};

export default GraphViewer;
