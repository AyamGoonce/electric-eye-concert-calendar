(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.623fdb767e3b509e.js","sha256":"623fdb767e3b509e8ae0cf35f856b5a560978e141d79481c759219f8d8e7fe19","count":244});
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
