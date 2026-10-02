(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.25aa7eecc53916cb.js","sha256":"25aa7eecc53916cb2051f6e734989ec0e92fe88347eeca742740ebe08eb95b21","count":244});
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
