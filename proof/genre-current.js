(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.431bce65c71997ab.js","sha256":"431bce65c71997abbbff78a7760b76f58eaeb37fb7877d9467d789f57d0678fc","count":247});
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
