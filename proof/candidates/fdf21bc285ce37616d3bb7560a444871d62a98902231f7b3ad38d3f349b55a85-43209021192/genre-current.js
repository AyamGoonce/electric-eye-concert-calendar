(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.c4acb23940f4d20c.js","sha256":"c4acb23940f4d20c2178ff7f17c75f3e2277eb667f1c984d498796fb1c0bcf60","count":244});
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
