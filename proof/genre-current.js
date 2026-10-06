(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.3a4b4dea8e8021a4.js","sha256":"3a4b4dea8e8021a455abc0a4f045e9ff688020830417d45c356e327c645d5efc","count":244});
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
