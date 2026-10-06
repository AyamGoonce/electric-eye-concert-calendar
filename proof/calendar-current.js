(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b33c9624067cb249.js","sha256":"b33c9624067cb24974c9600e2ef589914fc70e2c3a11ff15d52f5dce4ce38827","count":2214,"publishedAt":"2026-10-06T22:43:02Z","state":"calendar-state.json","stateSha256":"612592efc8ec44ffde77f5682660481397cad9245f52cd9d73f53dd7a75f458c","sourceState":"calendar-source-state.json","sourceStateSha256":"ac603089c2ec407f3ad6c61324084e72e7f8852431906cf0d7bcb3f2372aaac6"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
