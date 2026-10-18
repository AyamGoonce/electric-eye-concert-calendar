(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.5b9bb018a399c8eb.js","sha256":"5b9bb018a399c8eba8bb6a02dcd5ab7dfc3f37fc5becbc15852b21eb52d43687","count":244});
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
