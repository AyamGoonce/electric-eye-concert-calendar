(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.e9cff4aa9145884c.js","sha256":"e9cff4aa9145884c7eb7ee653f3bb895a761f4f26ae20d04f564fdae4e624114","count":244});
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
