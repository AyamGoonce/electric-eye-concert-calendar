(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.8ab048cc6d3fbb93.js","sha256":"8ab048cc6d3fbb934f0ab298f94462d3ca3e2b1dd297484fa18d249e8dfc4942","count":244});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeGenreManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:genre-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:genre-data-error", {detail:{reason:"genre data unavailable"}}));
  };
  document.head.appendChild(script);
}());
