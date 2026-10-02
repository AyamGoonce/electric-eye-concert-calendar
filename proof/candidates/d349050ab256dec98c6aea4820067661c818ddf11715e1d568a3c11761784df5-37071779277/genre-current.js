(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.328e7033c96ddf46.js","sha256":"328e7033c96ddf465bd12e8ce902d918bccb61c984a30158bd1ed1addc8ded31","count":247});
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
