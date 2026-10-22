(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.1129467d3f16a29b.js","sha256":"1129467d3f16a29b69a2ae217f7e72f154fcfae954c78e06048dc495bd0658c4","count":244});
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
