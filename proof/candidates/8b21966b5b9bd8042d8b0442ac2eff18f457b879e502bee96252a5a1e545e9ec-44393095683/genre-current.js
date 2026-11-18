(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.841a7aba8f4dfef8.js","sha256":"841a7aba8f4dfef8e66ef30d24ccb2435223ef9b1c02ccdbfdd021ae99a827f8","count":244});
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
