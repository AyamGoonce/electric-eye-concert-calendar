(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.9614296bff53c289.js","sha256":"9614296bff53c2894c7e06249bed11d6334c0ebc7b8c2f5bab00a2bf6ed68c6e","count":244});
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
