/**
 * Lightweight Markdown Renderer
 * Renders common markdown syntax without external dependencies
 */

import React from 'react';

const MarkdownRenderer = ({ content, className = '' }) => {
  const renderMarkdown = (text) => {
    if (!text) return null;

    // Split by lines to handle lists and paragraphs
    const lines = text.split('\n');
    const elements = [];
    let listItems = [];
    let listType = null;

    const flushList = () => {
      if (listItems.length > 0) {
        if (listType === 'ul') {
          elements.push(
            <ul key={`list-${elements.length}`} className="list-disc ml-5 mb-3 space-y-1">
              {listItems}
            </ul>
          );
        } else if (listType === 'ol') {
          elements.push(
            <ol key={`list-${elements.length}`} className="list-decimal ml-5 mb-3 space-y-1">
              {listItems}
            </ol>
          );
        }
        listItems = [];
        listType = null;
      }
    };

    const processInlineFormatting = (line) => {
      // Handle bold (**text** or __text__)
      let parts = [];
      let currentText = line;
      let key = 0;

      // Process bold
      const boldRegex = /(\*\*|__)(.*?)\1/g;
      let lastIndex = 0;
      let match;

      while ((match = boldRegex.exec(currentText)) !== null) {
        // Add text before match
        if (match.index > lastIndex) {
          parts.push(currentText.substring(lastIndex, match.index));
        }
        // Add bold text
        parts.push(<strong key={`bold-${key++}`}>{match[2]}</strong>);
        lastIndex = match.index + match[0].length;
      }

      // Add remaining text
      if (lastIndex < currentText.length) {
        parts.push(currentText.substring(lastIndex));
      }

      // If no formatting found, return original line
      return parts.length > 0 ? parts : line;
    };

    lines.forEach((line, index) => {
      // Handle headers
      if (line.startsWith('### ')) {
        flushList();
        elements.push(
          <h3 key={`h3-${index}`} className="font-bold text-base mb-2 mt-3">
            {processInlineFormatting(line.substring(4))}
          </h3>
        );
      } else if (line.startsWith('## ')) {
        flushList();
        elements.push(
          <h2 key={`h2-${index}`} className="font-bold text-lg mb-2 mt-3">
            {processInlineFormatting(line.substring(3))}
          </h2>
        );
      } else if (line.startsWith('# ')) {
        flushList();
        elements.push(
          <h1 key={`h1-${index}`} className="font-bold text-xl mb-2 mt-3">
            {processInlineFormatting(line.substring(2))}
          </h1>
        );
      }
      // Handle unordered lists
      else if (line.match(/^\s*[*-]\s+/)) {
        if (listType !== 'ul') {
          flushList();
          listType = 'ul';
        }
        const content = line.replace(/^\s*[*-]\s+/, '');
        listItems.push(
          <li key={`li-${index}`} className="text-sm">
            {processInlineFormatting(content)}
          </li>
        );
      }
      // Handle ordered lists
      else if (line.match(/^\s*\d+\.\s+/)) {
        if (listType !== 'ol') {
          flushList();
          listType = 'ol';
        }
        const content = line.replace(/^\s*\d+\.\s+/, '');
        listItems.push(
          <li key={`li-${index}`} className="text-sm">
            {processInlineFormatting(content)}
          </li>
        );
      }
      // Handle empty lines
      else if (line.trim() === '') {
        flushList();
        elements.push(<div key={`space-${index}`} className="h-2"></div>);
      }
      // Regular paragraphs
      else {
        flushList();
        elements.push(
          <p key={`p-${index}`} className="mb-2 text-sm">
            {processInlineFormatting(line)}
          </p>
        );
      }
    });

    // Flush any remaining list
    flushList();

    return elements;
  };

  return <div className={className}>{renderMarkdown(content)}</div>;
};

export default MarkdownRenderer;
