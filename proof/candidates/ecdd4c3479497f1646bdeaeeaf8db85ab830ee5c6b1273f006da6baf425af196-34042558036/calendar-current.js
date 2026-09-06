(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ecdd4c3479497f16.js","sha256":"ecdd4c3479497f1646bdeaeeaf8db85ab830ee5c6b1273f006da6baf425af196","count":2466,"publishedAt":"2026-09-06T15:39:28Z","state":"calendar-state.json","stateSha256":"a46885a4a21105043da8e2c2f9358445cd4daf7f86eee1829b54d851f64d1dee"});
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
