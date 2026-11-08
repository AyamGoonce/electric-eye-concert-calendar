(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.dc69ee3e3251593b.js","sha256":"dc69ee3e3251593b12e5e0ac978333771fb668074dc14f79c03c6e2e48163693","count":244});
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
