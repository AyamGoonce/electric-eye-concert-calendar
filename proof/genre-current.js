(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.8d5a1e1533ef3314.js","sha256":"8d5a1e1533ef33141d32d5cbf588a2395bd1bada63c1f5d931ad4dc08c8bdafc","count":244});
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
