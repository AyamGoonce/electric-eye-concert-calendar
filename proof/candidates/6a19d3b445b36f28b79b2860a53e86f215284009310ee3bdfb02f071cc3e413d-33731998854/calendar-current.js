(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.6a19d3b445b36f28.js","sha256":"6a19d3b445b36f28b79b2860a53e86f215284009310ee3bdfb02f071cc3e413d","count":2381,"publishedAt":"2026-09-03T08:19:39Z","state":"calendar-state.json","stateSha256":"9bbf6621c48ccc8f82e55e657eb69879f1aa87a80bd9add872697178d7b884c6"});
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
