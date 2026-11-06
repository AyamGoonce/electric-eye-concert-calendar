(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.b6a1519df16a8806.js","sha256":"b6a1519df16a880667ee2f626fbb90d2566d5cc09ad7b1c4b9e94b59fb4e4aaf","count":244});
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
