(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.717055e5b13a2fc8.js","sha256":"717055e5b13a2fc8685cc9ed54251db29a9555e448035d95c4cbcc66153ef068","count":244});
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
