(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3c0cce0e55ef5650.js","sha256":"3c0cce0e55ef5650fcf375e6326d60d1384b301dfd2abf57fb48f1e0462f1898","count":2147,"publishedAt":"2026-09-23T21:39:05Z","state":"calendar-state.json","stateSha256":"94008d1f9ab6585763043823c11ec9f2cf60519a6df4f4ec49348a26f02cc95c","sourceState":"calendar-source-state.json","sourceStateSha256":"fcc9191acfd829de0db3e0dd797354a61b6335b105a4640b0914f7299db6e974"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
